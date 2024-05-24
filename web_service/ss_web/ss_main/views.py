import openpyxl
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from datetime import timedelta
from .decorators.auth_decorators import staff_required
from .forms.auth_form import CustomAuthenticationForm
from .forms.forms import ReportFilterForm
from .models import Report, Cabinet


@staff_required
def main(request):
    cities = Cabinet.objects.values_list('city', flat=True).distinct()
    return render(request, 'ss_main/index.html', {'cities': cities})


def station_ids(request):
    query = request.GET.get('query', '')
    data = Report.objects.filter(stationid__icontains=query)
    suggestions = list(data.values_list('stationid', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


def cities(request):
    query = request.GET.get('query', '')
    data = Report.objects.filter(city__icontains=query)
    suggestions = list(data.values_list('city', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


def zones(request):
    query = request.GET.get('query', '')
    data = Report.objects.filter(zone__icontains=query)
    suggestions = list(data.values_list('zone', flat=True).distinct())
    return JsonResponse(suggestions, safe=False)


def report(request):
    if request.method == 'POST':
        form = ReportFilterForm(request.POST)
        if form.is_valid():
            select_all = form.cleaned_data.get('select_all')

            if select_all:
                reports = Report.objects.all()
            else:
                station_id = form.cleaned_data.get('station_id')
                city = form.cleaned_data.get('city')
                zone = form.cleaned_data.get('zone')
                time_from = form.cleaned_data.get('time_from')
                time_to = form.cleaned_data.get('time_to')

                # Проверяем, выбран ли хотя бы один фильтр
                if not any([station_id, city, zone, time_from, time_to]):
                    return HttpResponse("Пожалуйста, выберите хотя бы один фильтр.")

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
