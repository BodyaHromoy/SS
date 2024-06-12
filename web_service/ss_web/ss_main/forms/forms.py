from django import forms
from ..models import CustomUser


class ReportFilterForm(forms.Form):
    station_id = forms.CharField(label='Station ID', required=False,
                                 widget=forms.TextInput(attrs={'autocomplete': 'off', 'data-selected': '', 'class': 'autocomplete-input'}))
    city = forms.CharField(label='City', required=False, widget=forms.TextInput(attrs={'autocomplete': 'off', 'data-selected': '', 'class': 'autocomplete-input'}))
    zone = forms.CharField(label='Zone', required=False, widget=forms.TextInput(attrs={'autocomplete': 'off', 'data-selected': '', 'class': 'autocomplete-input'}))
    select_all = forms.BooleanField(label='Выбрать все', required=False)
    time_from = forms.DateField(label='Time From', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    time_to = forms.DateField(label='Time To', required=False, widget=forms.DateInput(attrs={'type': 'date'}))


class CourierCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.CharField(initial='courier', disabled=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'role']