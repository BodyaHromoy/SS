import json
import random
import string
from datetime import timedelta
import datetime
import pytz
from django.db.models.functions import Cast
import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.db.models import Count, Avg
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.db.models import F, FloatField
import paho.mqtt.client as mqtt
import logging
from .decorators.auth_decorators import staff_required
from .forms.auth_form import CustomAuthenticationForm
from .forms.forms import ReportFilterForm, CourierCreationForm, LogicCreationForm, CabinetSettingsForm, \
    SettingsForSettingsForm
from .models import *


logger = logging.getLogger(__name__)


def is_courier(user):
    return user.is_authenticated and user.role == 'courier' or 'engineer'


def is_logistician(user):
    return user.is_authenticated and user.role == 'logistician' or 'engineer'


def is_engineer(user):
    return user.is_authenticated and user.role == 'engineer'


def is_regional_manager(user):
    return user.is_authenticated and user.role == 'regional_manager' or 'engineer'


@user_passes_test(is_engineer)
def send_command(request):
    if request.method == 'POST':
        cabinet_id = request.POST.get('cabinet_id')
        endpoint_id = request.POST.get('endpoint_id')
        cmd_number = request.POST.get('cmd_number')

        try:
            if cmd_number == "del":
                deleted_count, _ = Cell.objects.filter(cabinet_id__shkaf_id=cabinet_id, endpointid=endpoint_id).delete()
                if deleted_count > 0:
                    return JsonResponse({"success": True, "message": "Запись успешно удалена!"})
                else:
                    return JsonResponse({"success": False, "message": "Запись не найдена для удаления."})

            record = Cell.objects.get(cabinet_id__shkaf_id=cabinet_id, endpointid=endpoint_id)

            if cmd_number == '1':
                record.is_error = True
                Marked.objects.create(sn=record.sn)
            elif cmd_number == '0':
                record.is_error = False
                Marked.objects.filter(sn=record.sn).delete()
            record.save()

            json_data = {
                "Type": "cmd",
                "StationID": int(record.cabinet_id_id),
                "EndpointID": int(record.endpointid),
                "CMD": int(cmd_number),
                "SN": record.sn
            }

            client = mqtt.Client()
            client.connect("192.168.1.98", 1883, 60)
            client.publish("test/back", json.dumps(json_data))
            client.disconnect()

            return JsonResponse({"success": True, "message": "Команда отправлена успешно!"})
        except Cell.DoesNotExist:
            return JsonResponse({"success": False, "message": "Ячейка не найдена."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Ошибка при обработке команды: {str(e)}"})
    return JsonResponse({"success": False, "message": "Неверный запрос."})


@user_passes_test(is_engineer)
def new_eng(request):
    cabinets = Cabinet.objects.all()
    cities = City.objects.all()
    zones = Zone.objects.all()
    return render(request, 'ss_main/new_eng.html', {'cabinets': cabinets, 'cities': cities, 'zones': zones})


@user_passes_test(is_engineer)
def new_eng_cabinet_detail(request, shkaf_id):
    cabinet = get_object_or_404(Cabinet, shkaf_id=shkaf_id)
    cells = Cell.objects.filter(cabinet_id=cabinet).order_by('endpointid')
    return render(request, 'ss_main/new_eng_cabinet_detail.html', {'cabinet': cabinet, 'cells': cells})


@user_passes_test(is_engineer)
def cabinet_settings(request, shkaf_id):
    cabinet = get_object_or_404(Cabinet, shkaf_id=shkaf_id)
    settings = Cabinet_settings_for_auto_marking.objects.filter(cabinet_id=cabinet).first()
    settings_for_settings = Settings_for_settings.objects.filter(settings_for=settings).first()

    if request.method == 'POST':
        form = CabinetSettingsForm(request.POST, instance=settings)
        settings_for_form = SettingsForSettingsForm(request.POST, instance=settings_for_settings)

        if form.is_valid() and settings_for_form.is_valid():
            form.save()
            settings_for_form.save()

            Cell.objects.filter(cabinet_id=cabinet).update(is_error=False)
            Cell.objects.filter(cabinet_id=cabinet).update(message=None)

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': {**form.errors, **settings_for_form.errors}})

    form = CabinetSettingsForm(instance=settings)
    settings_for_form = SettingsForSettingsForm(instance=settings_for_settings)

    return render(request, 'ss_main/cabinet_settings_partial.html', {
        'form': form,
        'settings_for_form': settings_for_form,
        'cabinet': cabinet
    })


@user_passes_test(is_engineer)
def main(request):
    cities = Cabinet.objects.values_list('city', flat=True).distinct()
    return render(request, 'ss_main/index.html', {'cities': cities})


# Регистрация нового курьера
@login_required
@user_passes_test(is_logistician)
def create_courier(request):
    #if not request.user.role == 'logistician':
     #   return HttpResponseForbidden()

    if request.method == 'POST':
        form = CourierCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
            user.set_password(password)
            user.username = f'{user.first_name}_{user.last_name}'
            user.save()

            current_user_citys = request.user.citys.all()
            for city in current_user_citys:
                user.citys.add(city)

            send_mail(
                'Scout Registration Info',
                f'Username: {user.username}\nPassword: {password}\nEmail: {user.email}\nFull Name: {user.first_name} {user.last_name}',
                'bhromenko@mail.ru',
                [request.user.email],
                fail_silently=False,
            )
            messages.success(request, f"Скаут '{user.username}' успешно зарегистрирован (проверьте свою почту).")
    else:
        form = CourierCreationForm()

    return render(request, 'ss_main/create_courier.html', {'form': form})


# Создание нового логиста
@login_required
@user_passes_test(is_regional_manager)
def create_logic(request):
    if not request.user.role == 'regional_manager':
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = LogicCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
            user.set_password(password)
            user.username = f'{user.first_name}_{user.last_name}'
            user.save()

            send_mail(
                'Logistician Registration Info',
                f'Username: {user.username}\nPassword: {password}\nEmail: {user.email}\nFull Name: {user.first_name} {user.last_name}',
                'bhromenko@mail.ru',
                [request.user.email],
                fail_silently=False,
            )
            messages.success(request, f"Logistician '{user.username}' successfully registered (check your email).")
    else:
        form = LogicCreationForm()

    return render(request, 'ss_main/create_logic.html', {'form': form})


# Назначение зоны курьеру
@login_required
@user_passes_test(is_logistician)
def assign_zone_to_courier(request):
    user_city = request.user.citys.first()
    if request.method == 'POST':
        courier_id = request.POST.get('courier_id')
        zone_id = request.POST.get('zone_id')
        try:
            courier = get_object_or_404(CustomUser, pk=courier_id)
            zone = get_object_or_404(Zone, pk=zone_id)
            if zone.city == user_city:
                courier.zones.clear()
                courier.zones.add(zone)
                messages.success(request, f"Zone '{zone.zone_name}' successfully assigned to courier '{courier.username}'.")
            else:
                messages.error(request, "The selected zone is not in your city.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('assign_zone_to_courier')

    couriers = CustomUser.objects.filter(role='courier', citys=user_city)
    zones = Zone.objects.filter(city=user_city)
    return render(request, 'ss_main/assign_zone.html', {'couriers': couriers, 'zones': zones})


# Удаление курьера
@login_required
@user_passes_test(is_logistician)
def delete_courier(request, courier_id):
    courier = get_object_or_404(CustomUser, pk=courier_id)
    courier.delete()
    return JsonResponse({'status': 'success'})


# Назначение зоны зоны логисту
@login_required
@user_passes_test(is_regional_manager)
def assign_zone_to_logic(request):
    if request.method == 'POST':
        logistician_id = request.POST.get('logistician_id')
        zone_id = request.POST.get('zone_id')

        try:
            logistician = get_object_or_404(CustomUser, pk=logistician_id)
            zone = get_object_or_404(Zone, pk=zone_id)

            logistician.zones.clear()
            logistician.zones.add(zone)
            messages.success(request, f"Zone '{zone.zone_name}' successfully assigned to logistician '{logistician.username}'.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('assign_zone_to_logic')

    logisticians = CustomUser.objects.filter(role='logistician')
    zones = Zone.objects.all()
    return render(request, 'ss_main/assign_logic.html', {'logisticians': logisticians, 'zones': zones})


# Список зон (основная страница логиста)
@login_required
@user_passes_test(is_logistician)
def zone_list(request):
    user = request.user
    user_city = user.citys.first()
    if user_city:
        zones = Zone.objects.filter(city=user_city)
    else:
        zones = Zone.objects.none()

    zone_data = []

    for zone in zones:
        cabinets = Cabinet.objects.filter(zone=zone)
        status_counts = {
            'ready': 0,
            'charging': 0,
            'empty': 0,
            'Inactive': 0
        }

        for cabinet in cabinets:
            cells = Cell.objects.filter(cabinet_id=cabinet)
            for cell in cells:
                if cell.status == 'ready':
                    status_counts['ready'] += 1
                elif cell.status == 'charging':
                    status_counts['charging'] += 1
                elif cell.status == 'empty':
                    status_counts['empty'] += 1
                elif cell.status == 'Inactive':
                    status_counts['Inactive'] += 1

        zone_data.append({
            'zone': zone,
            'status_counts': status_counts,
            'user': user
        })

    return render(request, 'ss_main/zone_list.html', {'zone_data': zone_data, 'user_city': user_city})


# Список курьеров в зоне(у логиста)
@login_required
@user_passes_test(is_logistician)
def zone_detail(request, zone_id):
    zone = get_object_or_404(Zone, id=zone_id)
    couriers = CustomUser.objects.filter(zones=zone, role='courier')
    return render(request, 'ss_main/zone_detail.html', {'zone': zone, 'couriers': couriers})


# Список шкафов в зоне(у логиста)
@login_required
@user_passes_test(is_logistician)
def cabinet_list(request, zone_id):
    zone = get_object_or_404(Zone, pk=zone_id)
    cabinets = Cabinet.objects.filter(zone=zone)
    cabinets_count = cabinets.count()

    total_cells_count = 0
    cabinets_status_counts = []
    for cabinet in cabinets:
        cells = Cell.objects.filter(cabinet_id=cabinet)
        total_cells_count += cells.count()
        status_counts = {
            'ready': cells.filter(status='ready').count(),
            'charging': cells.filter(status='charging').count(),
            'empty': cells.filter(status='empty').count(),
            'Inactive': cells.filter(status='Inactive').count(),
            'ban': cells.filter(status='BAN').count(),
        }
        cabinets_status_counts.append((cabinet, status_counts))

    return render(request, 'ss_main/cabinet_list.html', {
        'zone': zone,
        'cabinets_count': cabinets_count,
        'total_cells_count': total_cells_count,

        'cabinets_status_counts': cabinets_status_counts,
    })


# Обновление деталий шкафа
def cabinet_details_api(request, shkaf_id):
    cabinet = get_object_or_404(Cabinet, shkaf_id=shkaf_id, zone__users=request.user)
    cells = Cell.objects.filter(cabinet_id=cabinet)

    cabinet_data = {
        'shkaf_id': cabinet.shkaf_id,
        'city': {'city_name': cabinet.city.city_name},
        'zone': {'zone_name': cabinet.zone.zone_name},
        'street': cabinet.street,
        'location': cabinet.location,
        'extra_inf': cabinet.extra_inf,
        'cells': [
            {'endpointid': cell.endpointid, 'cap_percent': cell.cap_percent, 'vid': cell.vid}
            for cell in cells
        ]
    }

    return JsonResponse(cabinet_data)


# Основная страница регионального менеджера
@login_required
@user_passes_test(is_regional_manager)
def main_region(request):
    cities = City.objects.all()
    city_data = []
    for city in cities:
        zones_count = Zone.objects.filter(city=city).count()
        cabinets_count = Cabinet.objects.filter(city=city).count()
        city_data.append({
            'city': city,
            'zones_count': zones_count,
            'cabinets_count': cabinets_count,
        })
    return render(request, 'ss_main/main_region.html', {'city_data': city_data, 'cities': cities})


# Список зон в городе(региональный менеджер)
@login_required
@user_passes_test(is_regional_manager)
def region_zones(request, city_id):
    city = get_object_or_404(City, id=city_id)
    zones = Zone.objects.filter(city=city)
    zone_data = []
    total_cells = 0
    total_cabinets = 0
    for zone in zones:
        status_counts = zone.cell_status_counts()
        total_cells += sum(status_counts.values())
        cabinets_count = Cabinet.objects.filter(zone=zone).count()
        total_cabinets += cabinets_count
        couriers_count = CustomUser.objects.filter(zones=zone, role='courier').count()
        logisticians_count = CustomUser.objects.filter(zones=zone, role='logistician').count()
        zone_data.append({
            'zone': zone,
            'status_counts': status_counts,
            'cabinets_count': cabinets_count,
            'couriers_count': couriers_count,
            'logisticians_count': logisticians_count
        })
    return render(request, 'ss_main/region_zones.html', {'zone_data': zone_data, 'city': city,
                                                         'total_zones': len(zone_data), 'total_cells': total_cells,
                                                         'total_cabinets': total_cabinets})


# Логисты зоны(региональный менеджер)
@login_required
@user_passes_test(is_regional_manager)
def region_logic(request, zone_id):
    zone = get_object_or_404(Zone, id=zone_id)
    logisticians = CustomUser.objects.filter(zones=zone, role='logistician').values('username', 'last_login',
                                                                                    'first_name', 'last_name')
    cabinets = Cabinet.objects.filter(zone=zone)
    cells = Cell.objects.filter(cabinet_id__in=cabinets)
    return render(request, 'ss_main/region_logic.html',
                  {'zone': zone, 'logisticians': logisticians, 'cabinets_count': cabinets.count(),
                   'cells_count': cells.count()})


# Основная страница курьера
@login_required
@user_passes_test(is_courier)
def user_cabinets(request):
    user = request.user
    zones = user.zones.all()
    cabinets = Cabinet.objects.filter(zone__in=zones)

    cabinet_statuses = []
    for cabinet in cabinets:
        cells = cabinet.cell_set.all()
        ready_count = cells.filter(status='ready').count()
        charging_count = cells.filter(status='charging').count()
        empty_count = cells.filter(status='empty').count()
        ban_count = cells.filter(status='BAN').count()
        cabinet_statuses.append({
            'cabinet': cabinet,
            'ready_count': ready_count,
            'charging_count': charging_count,
            'empty_count': empty_count,
            'ban_count': ban_count
        })

    context = {
        'cabinet_statuses': cabinet_statuses,
        'user': user,
        'zones': zones,
    }
    return render(request, 'ss_main/user_cabinets.html', context)


@login_required
def cabinet_details(request, shkaf_id):
    cabinet = get_object_or_404(Cabinet, shkaf_id=shkaf_id, zone__users=request.user)
    cells = Cell.objects.filter(cabinet_id=cabinet)
    status_counts = cells.values('status').annotate(count=Count('status')).order_by('status')
    status_slots = {}

    for cell in cells:
        status = cell.status
        endpointid = cell.endpointid
        sw_name = cell.sw_name
        cap_percent = cell.cap_percent or "N/A"
        if status not in status_slots:
            status_slots[status] = []
        status_slots[status].append({'endpointid': endpointid, 'charge': cap_percent, 'sw_name': sw_name})

    average_charge = cells.annotate(cap_percent_as_float=Cast('cap_percent', FloatField())).aggregate(
        average_charge=Avg('cap_percent_as_float'))['average_charge']

    error_slots = cells.filter(is_error=True)

    # Получаем текущую дату
    almaty_timezone = pytz.timezone('Asia/Almaty')
    current_time = datetime.datetime.now(almaty_timezone).replace(tzinfo=None)
    history_date = current_time.date()

    # Получаем запись из истории для текущей даты
    history_entry = Cabinet_history.objects.filter(history_for=cabinet, date=history_date).first()

    # Получаем количество за первую и вторую половину дня
    first_half_count = history_entry.first_half if history_entry else 0
    second_half_count = history_entry.second_half if history_entry else 0

    context = {
        'cabinet': cabinet,
        'status_counts': json.dumps(list(status_counts)),
        'status_slots': json.dumps(status_slots),
        'average_charge': average_charge,
        'error_slots': error_slots,
        'first_half_count': first_half_count,
        'second_half_count': second_half_count,
        'latitude': cabinet.latitude,
        'longitude': cabinet.longitude,
    }
    return render(request, 'ss_main/scout_v2.html', context)


# Обновление деталей шкафа
def update_cabinet_data(request, shkaf_id):
    logger.debug(f"Headers: {request.headers}")
    logger.debug(f"Method: {request.method}")
    cabinet = get_object_or_404(Cabinet, shkaf_id=shkaf_id, zone__users=request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cells = Cell.objects.filter(cabinet_id=cabinet)

        status_counts = cells.values('status').annotate(count=Count('status'))
        average_charge = cells.annotate(cap_percent_as_float=Cast('cap_percent', FloatField())).aggregate(
            average_charge=Avg('cap_percent_as_float'))['average_charge']

        status_slots = {}
        for cell in cells:
            status = cell.status
            if status not in status_slots:
                status_slots[status] = []
            status_slots[status].append({'endpointid': cell.endpointid, 'charge': cell.cap_percent, 'sw_name': cell.sw_name})
        error_slots = cells.filter(is_error=True)
        error_slots_list = [{'endpointid': slot.endpointid, 'message': slot.message} for slot in error_slots]
        almaty_timezone = pytz.timezone('Asia/Almaty')
        current_time = datetime.datetime.now(almaty_timezone).replace(tzinfo=None)
        history_date = current_time.date()
        history_entry = Cabinet_history.objects.filter(history_for=cabinet, date=history_date).first()
        first_half_count = history_entry.first_half if history_entry else 0
        second_half_count = history_entry.second_half if history_entry else 0
        return JsonResponse({
            'status_counts': list(status_counts),
            'status_slots': status_slots,
            'average_charge': average_charge,
            'error_slots': error_slots_list,
            'first_half_count': first_half_count,
            'second_half_count': second_half_count,
            'latitude': cabinet.latitude,
            'longitude': cabinet.longitude,
        })
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


# API для получения информации о статусах ячеек в шкафах
@login_required
def user_cabinets_api(request):
    user = request.user
    zones = user.zones.all()
    cabinets = Cabinet.objects.filter(zone__in=zones)

    cabinet_statuses = []
    for cabinet in cabinets:
        cells = cabinet.cell_set.all()
        ready_count = cells.filter(status='ready').count()
        charging_count = cells.filter(status='charging').count()
        empty_count = cells.filter(status='empty').count()
        ban_count = cells.filter(status='BAN').count()
        cabinet_statuses.append({
            'shkaf_id': cabinet.shkaf_id,
            'ready_count': ready_count,
            'charging_count': charging_count,
            'empty_count': empty_count,
            'ban_count': ban_count,
        })

    return JsonResponse(cabinet_statuses, safe=False)


# API для получения информации о статусах ячеек в шкафе
def station_ids(request):
    query = request.GET.get('query', '')
    data = Report.objects.using('new_db').filter(stationid__icontains=query)
    suggestions = list(data.values_list('stationid', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


# API для получения информации о городах
def cities(request):
    query = request.GET.get('query', '')
    data = Report.objects.using('new_db').filter(city__icontains=query)
    suggestions = list(data.values_list('city', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


# API для получения информации о зонах
def zones(request):
    query = request.GET.get('query', '')
    data = Report.objects.using('new_db').filter(zone__icontains=query)
    suggestions = list(data.values_list('zone', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


# Генерация отчета(моя гордость)
@staff_required
def report(request):
    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            station_id = form.cleaned_data.get('station_id')
            city = form.cleaned_data.get('city')
            zone = form.cleaned_data.get('zone')
            time_from = form.cleaned_data.get('time_from')
            time_to = form.cleaned_data.get('time_to')

            # Проверяем, выбраны ли все фильтры
            if not all([station_id, city, zone, time_from, time_to]):
                return HttpResponse("Пожалуйста, выберитpе все фильтры.")

            reports = Report.objects.using('new_db').all()

            if station_id:
                reports = reports.filter(stationid__startswith=station_id)
            if city:
                reports = reports.filter(city=city)
            if zone:
                reports = reports.filter(zone=zone)
            if time_from and time_to:
                time_to += timedelta(days=1)
                reports = reports.filter(time__range=[time_from, time_to])

                reports = reports.filter(time__range=[time_from, time_to])

            if reports.exists():
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="reports.xlsx"'

                workbook = openpyxl.Workbook()
                worksheet = workbook.active

                headers = ['city', 'zone', 'stationid', 'reason', 'balance_status', 'capacity', 'cap_coulo',
                           'cap_percent', 'cap_vol', 'charge_cap_h', 'charge_cap_l', 'charge_times', 'core_volt',
                           'current_cur', 'cycle_times', 'design_voltage', 'fun_boolean', 'healthy', 'ochg_state',
                           'odis_state', 'over_discharge_times', 'pcb_ver', 'remaining_cap', 'remaining_cap_percent',
                           'sn', 'sw_ver', 'temp_cur1', 'temp_cur2', 'total_capacity', 'vid', 'voltage_cur',
                           'session_start', "start_percent", 'time']
                worksheet.append(headers)


                for report in reports:
                    row = [report.city, report.zone, report.stationid, report.reason, report.balance_status,
                           report.capacity, report.cap_coulo, report.cap_percent, report.cap_vol, report.charge_cap_h,
                           report.charge_cap_l, report.charge_times, report.core_volt, report.current_cur,
                           report.cycle_times, report.design_voltage, report.fun_boolean, report.healthy,
                           report.ochg_state, report.odis_state, report.over_discharge_times, report.pcb_ver,
                           report.remaining_cap, report.remaining_cap_percent, report.sn, report.sw_ver,
                           report.temp_cur1, report.temp_cur2, report.total_capacity, report.vid, report.voltage_cur,
                           report.session_start.replace(tzinfo=None) if report.session_start else None,
                           report.start_percent,
                           report.time.replace(tzinfo=None) if report.time else None]
                    worksheet.append(row)


                workbook.save(response)
                return response
            else:
                return HttpResponse("Для выбранной зарядной станции, города или зоны отчеты отсутствуют.")
    else:
        form = ReportFilterForm()
        prefixes = Report.objects.using('new_db').values_list('stationid', flat=True).distinct()
        prefixes = set(prefix.split('-')[0] for prefix in prefixes)
        cities = Report.objects.using('new_db').values_list('city', flat=True).distinct()
        zones = Report.objects.using('new_db').values_list('zone', flat=True).distinct()

        return render(request, 'ss_main/report.html', {
            'form': form,
            'station_ids': list(prefixes),
            'cities': list(cities),
            'zones': list(zones)
        })


def reset_selection(request):
    if request.method == 'GET':
        if 'station_id' in request.session:
            del request.session['station_id']
        if 'select_all' in request.session:
            del request.session['select_all']
    return redirect('report')


# Авторизация
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'ss_main/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'courier':
            return '/my-cabinets/'
        elif user.role == 'logistician':
            return '/zones/'
        elif user.role == 'regional_manager':
            return '/region/'
        elif user.role == 'engineer':
            return '/'
        else:
            return '/'


class CustomLogoutView(LogoutView):
    next_page = '/'
    http_method_names = ['post']
