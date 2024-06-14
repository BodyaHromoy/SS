from datetime import timedelta

import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from .decorators.auth_decorators import staff_required
from .forms.auth_form import CustomAuthenticationForm
from .forms.forms import ReportFilterForm, CourierCreationForm
from .models import *


# Проверка на то является ли пользователь логистом
def is_logistician(user):
    return user.is_authenticated and user.role == 'logistician'


def is_regional_manager(user):
    return user.is_authenticated and user.role == 'regional_manager'


# Главная страница(инженерная)
@staff_required
def main(request):
    cities = Cabinet.objects.values_list('city', flat=True).distinct()
    return render(request, 'ss_main/index.html', {'cities': cities})


# Регистрация нового курьера
@login_required
@user_passes_test(is_logistician)
def create_courier(request):
    if not request.user.role == 'logistician':
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CourierCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('courier_list')
    else:
        form = CourierCreationForm()

    return render(request, 'ss_main/create_courier.html', {'form': form})


# Назначение зоны курьеру
@login_required
@user_passes_test(lambda u: u.role == 'logistician')
def assign_zone_to_courier(request):
    if request.method == 'POST':
        courier_id = request.POST.get('courier_id')
        zone_id = request.POST.get('zone_id')

        try:
            courier = get_object_or_404(CustomUser, pk=courier_id)
            zone = get_object_or_404(Zone, pk=zone_id)

            # Убедимся, что назначаем только одну зону
            courier.zones.clear()
            courier.zones.add(zone)
            messages.success(request, f"Zone '{zone.zone_name}' successfully assigned to courier '{courier.username}'.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('assign_zone_to_courier')

    couriers = CustomUser.objects.filter(role='courier')
    zones = Zone.objects.all()
    return render(request, 'ss_main/assign_zone.html', {'couriers': couriers, 'zones': zones})


# Список зон (основная страница логиста)
@login_required
@user_passes_test(is_logistician)
def zone_list(request):
    user = request.user
    zones = Zone.objects.all()
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

    return render(request, 'ss_main/zone_list.html', {'zone_data': zone_data})


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
    return render(request, 'ss_main/cabinet_list.html', {'zone': zone, 'cabinets': cabinets})


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


# Основная страница курьера
@login_required
def user_cabinets(request):
    # Получаем текущего пользователя
    user = request.user
    # Получаем все зоны, доступные пользователю
    zones = user.zones.all()
    # Получаем все шкафы, относящиеся к этим зонам
    cabinets = Cabinet.objects.filter(zone__in=zones)

    # Список для хранения информации о статусах в каждом шкафе
    cabinet_statuses = []
    # Проходимся по каждому шкафу
    for cabinet in cabinets:
        # Получаем все ячейки в текущем шкафе
        cells = cabinet.cell_set.all()
        # Считаем количество ячеек с каждым из статусов
        ready_count = cells.filter(status='ready').count()
        charging_count = cells.filter(status='charging').count()
        empty_count = cells.filter(status='empty').count()
        # Добавляем информацию о статусах в текущем шкафе в список
        cabinet_statuses.append({
            'cabinet': cabinet,
            'ready_count': ready_count,
            'charging_count': charging_count,
            'empty_count': empty_count,
        })

    context = {
        'cabinet_statuses': cabinet_statuses,
        'user': user,
        'zones': zones,
    }
    return render(request, 'ss_main/user_cabinets.html', context)


# Детали шкафа
def cabinet_details(request, shkaf_id):
    cabinet = get_object_or_404(Cabinet, shkaf_id=shkaf_id, zone__users=request.user)
    cells = Cell.objects.filter(cabinet_id=cabinet)
    context = {
        'cabinet': cabinet,
        'cells': cells,
    }
    return render(request, 'ss_main/cabinet_details.html', context)


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
        cabinet_statuses.append({
            'shkaf_id': cabinet.shkaf_id,
            'ready_count': ready_count,
            'charging_count': charging_count,
            'empty_count': empty_count,
        })

    return JsonResponse(cabinet_statuses, safe=False)


# API для получения информации о статусах ячеек в шкафе
def station_ids(request):
    query = request.GET.get('query', '')
    data = Report.objects.filter(stationid__icontains=query)
    suggestions = list(data.values_list('stationid', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


# API для получения информации о городах
def cities(request):
    query = request.GET.get('query', '')
    data = Report.objects.filter(city__icontains=query)
    suggestions = list(data.values_list('city', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


# API для получения информации о зонах
def zones(request):
    query = request.GET.get('query', '')
    data = Report.objects.filter(zone__icontains=query)
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
                return HttpResponse("Пожалуйста, выберите все фильтры.")

            reports = Report.objects.all()

            if station_id:
                reports = reports.filter(stationid__startswith=station_id)
            if city:
                reports = reports.filter(city=city)
            if zone:
                reports = reports.filter(zone=zone)
            if time_from and time_to:
                time_to += timedelta(days=1)  # Добавляем один день к конечной дате
                reports = reports.filter(time__range=[time_from, time_to])

            if reports:
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="reports.xlsx"'

                workbook = openpyxl.Workbook()
                worksheet = workbook.active

                headers = ['city', 'zone', 'stationid', 'reason', 'balance_status', 'capacity', 'cap_coulo',
                           'cap_percent',
                           'cap_vol', 'charge_cap_h', 'charge_cap_l', 'charge_times', 'core_volt',
                           'current_cur', 'cycle_times', 'design_voltage', 'fun_boolean', 'healthy',
                           'ochg_state', 'odis_state', 'over_discharge_times', 'pcb_ver',
                           'remaining_cap', 'remaining_cap_percent', 'sn', 'sw_ver', 'temp_cur1',
                           'temp_cur2', 'total_capacity', 'vid', 'voltage_cur', 'session_start',
                           'session_end']
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
                           report.time.replace(tzinfo=None) if report.time else None]
                    worksheet.append(row)

                workbook.save(response)
                return response
            else:
                return HttpResponse("Для выбранной зарядной станции, города или зоны отчеты отсутствуют.")
    else:
        form = ReportFilterForm()
        prefixes = Report.objects.values_list('stationid', flat=True).distinct()
        prefixes = set(prefix.split('-')[0] for prefix in prefixes)
        cities = Report.objects.values_list('city', flat=True).distinct()
        zones = Report.objects.values_list('zone', flat=True).distinct()

        return render(request, 'ss_main/report.html', {
            'form': form,
            'station_ids': list(prefixes),
            'cities': list(cities),
            'zones': list(zones)
        })


def reset_selection(request):
    if request.method == 'GET':
        # Очищаем значения выбора станции и чекбокса "Выбрать все" из сессии
        if 'station_id' in request.session:
            del request.session['station_id']
        if 'select_all' in request.session:
            del request.session['select_all']
    # Перенаправляем пользователя обратно на страницу отчета
    return redirect('report')


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'ss_main/login.html'

    def get_success_url(self):
        return self.request.GET.get('next', '/')


class CustomLogoutView(LogoutView):
    next_page = '/'
    http_method_names = ['post']
