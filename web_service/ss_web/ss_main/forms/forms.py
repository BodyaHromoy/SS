# ss_main/forms.py
from django import forms
from ..models import Report

class ReportFilterForm(forms.Form):
    station_id = forms.ModelMultipleChoiceField(queryset=Report.objects.values_list('stationid', flat=True).distinct(), label='Station ID', required=False)
    city = forms.ModelMultipleChoiceField(queryset=Report.objects.values_list('city', flat=True).distinct(), label='City', required=False)
    zone = forms.ModelMultipleChoiceField(queryset=Report.objects.values_list('zone', flat=True).distinct(), label='Zone', required=False)
    select_all = forms.BooleanField(label='Выбрать все', required=False)