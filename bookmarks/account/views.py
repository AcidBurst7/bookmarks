from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from .forms import LoginForm


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html',
        {'section': 'dashboard'}
    )


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Авторизация прошла успешно!')
                else:
                    return HttpResponse('Аккаунт с такми логином и паролем не существует.')
            else:
                return HttpResponse('Неверно введен логин или пароль.')
        else:
            return HttpResponse('Введенные данные некорректны')
    else:
        form = LoginForm()
    return render(
        request,
        'account/login.html',
        {'form': form}
    )
