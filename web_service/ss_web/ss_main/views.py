import openpyxl
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .decorators.auth_decorators import staff_required
from .forms.auth_form import CustomAuthenticationForm
from .models import Report


@staff_required
def main(request):
    return render(request, 'ss_main/base.html', {})


@staff_required
def report(request):
    if request.method == 'POST':
        station_ids = request.POST.getlist('station_id')
        select_all = request.POST.get('select_all')
        cities = request.POST.getlist('city')
        zones = request.POST.getlist('zone')

        reports = Report.objects.all()

        if not station_ids and not select_all and not cities and not zones:
            return HttpResponse("Пожалуйста, выберите зарядную станцию, город или зону, либо отметьте 'Выбрать все'.")

        if select_all:
            reports = Report.objects.all()
        else:
            if station_ids:
                reports = reports.filter(
                    stationid__in=[
                        report.stationid for report in Report.objects.all()
                        if any(report.stationid.startswith(prefix) for prefix in station_ids)
                    ]
                )
            if cities:
                reports = reports.filter(city__in=cities)
            if zones:
                reports = reports.filter(zone__in=zones)

        if reports.exists():
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="reports.xlsx"'

            workbook = openpyxl.Workbook()
            worksheet = workbook.active

            headers = ['stationid', 'balance_status', 'capacity', 'cap_coulo', 'cap_percent',
                       'cap_vol', 'charge_cap_h', 'charge_cap_l', 'charge_times', 'core_volt',
                       'current_cur', 'cycle_times', 'design_voltage', 'fun_boolean', 'healthy',
                       'ochg_state', 'odis_state', 'over_discharge_times', 'pcb_ver',
                       'remaining_cap', 'remaining_cap_percent', 'sn', 'sw_ver', 'temp_cur1',
                       'temp_cur2', 'total_capacity', 'vid', 'voltage_cur', 'session_start',
                       'session_end', 'reason', 'city', 'zone']
            worksheet.append(headers)

            for report in reports:
                row = [report.stationid, report.balance_status, report.capacity, report.cap_coulo,
                       report.cap_percent, report.cap_vol, report.charge_cap_h, report.charge_cap_l,
                       report.charge_times, report.core_volt, report.current_cur, report.cycle_times,
                       report.design_voltage, report.fun_boolean, report.healthy, report.ochg_state,
                       report.odis_state, report.over_discharge_times, report.pcb_ver, report.remaining_cap,
                       report.remaining_cap_percent, report.sn, report.sw_ver, report.temp_cur1,
                       report.temp_cur2, report.total_capacity, report.vid, report.voltage_cur,
                       report.session_start.replace(tzinfo=None) if report.session_start else None,
                       report.time.replace(tzinfo=None) if report.time else None, report.reason, report.city,
                       report.zone]
                worksheet.append(row)

            workbook.save(response)
            return response
        else:
            return HttpResponse("Для выбранной зарядной станции, города или зоны отчеты отсутствуют.")
    else:
        # Extract unique prefixes for stationid
        prefixes = set()
        for report in Report.objects.all():
            prefix = report.stationid.split('-')[0]
            prefixes.add(prefix)

        cities = Report.objects.values_list('city', flat=True).distinct()
        zones = Report.objects.values_list('zone', flat=True).distinct()

        return render(request, 'ss_main/report.html', {'station_ids': prefixes, 'cities': cities, 'zones': zones})


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
