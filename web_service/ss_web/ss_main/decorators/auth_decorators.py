from django.contrib.auth.decorators import login_required


def staff_required(function=None, redirect_field_name='next', login_url="/login"):
    return login_required(function, redirect_field_name=redirect_field_name, login_url=login_url)
