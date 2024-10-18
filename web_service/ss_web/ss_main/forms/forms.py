from django import forms
from ..models import *


class CabinetSettingsForm(forms.ModelForm):
    class Meta:
        model = Cabinet_settings_for_auto_marking
        fields = [
            'sn_error', 'year_of_manufacture', 'max_cycle_times', 'vid',
            'sw_ver', 'critical_temp', 'temp_inside', 'mains_voltage',
            'reserve_voltage', 'lock_status', 'fan_status'
        ]


class ReportFilterForm(forms.Form):
    station_id = forms.CharField(label='Station ID', required=False,
                                 widget=forms.TextInput(attrs={'autocomplete': 'off', 'data-selected': '', 'class': 'autocomplete-input'}))
    city = forms.CharField(label='City', required=False, widget=forms.TextInput(attrs={'autocomplete': 'off', 'data-selected': '', 'class': 'autocomplete-input'}))
    zone = forms.CharField(label='Zone', required=False, widget=forms.TextInput(attrs={'autocomplete': 'off', 'data-selected': '', 'class': 'autocomplete-input'}))
    select_all = forms.BooleanField(label='Выбрать все', required=False)
    time_from = forms.DateField(label='Time From', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    time_to = forms.DateField(label='Time To', required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class CourierCreationForm(forms.ModelForm):
    role = forms.CharField(initial='courier', disabled=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role']


class LogicCreationForm(forms.ModelForm):
    role = forms.CharField(initial='logistician', disabled=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role']