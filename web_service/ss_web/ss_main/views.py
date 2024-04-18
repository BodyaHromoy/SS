from django.shortcuts import render
from .models import City


def main(request):
    context = {'citys': City.objects.all()}
    return render(request, 'ss_main/base.html', context=context)
