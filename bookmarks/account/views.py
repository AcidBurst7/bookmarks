from django.contrib import messages
from django.contrib.auth import authenticate, login,  get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from actions.utils import create_action
from .forms import (
    LoginForm, 
    UserRegistrationForm,
    UserEditForm,
    ProfileEditForm
)
from .models import Profile, Contact
from actions.models import Action

User = get_user_model()


@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile')\
                    .prefetch_related('target')[:10]
    return render(request, 'account/dashboard.html',
        {'section': 'dashboard', 'actions': actions}
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


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(
                form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(request.user, 'новый пользователь')
            return render(
                request,
                'account/register_done.html',
                {'form': form}
            )
    else:
        form = UserRegistrationForm()
    return render(
                request,
                'account/register.html',
                {'form': form}
            )


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user, 
            data=request.POST
        )

        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST, 
            files=request.FILES
        )
            
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Профиль успешно обновлен.")
        else:
            messages.error(request, "Ошибка при обновлении профиля.")
        return render(
                request, 
                'account/dashboard.html',
                {'section': 'dashboard'}
            )
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(
        request,
        'account/edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )


@login_required
def users_list(request):
    users = User.objects.filter(is_active=True).filter(is_staff=False)
    return render(
        request,
        'account/user/list.html',
        {'section': 'people', 'users': users}
    )


@login_required
def user_detail(request, username):
    user = get_object_or_404(User, is_active=True, username=username)
    return render(
        request,
        'account/user/detail.html',
        {'section': 'people', 'user': user}
    )


@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'пользователь подписался', user)
            else:
                Contact.objects.filter(
                    user_from=request.user,
                    user_to=user
                ).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})