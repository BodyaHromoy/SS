from django.shortcuts import redirect, render


def main(request):
    return render(request, 'ss_main/base.html', {})
