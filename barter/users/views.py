from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from users import (
    constants as users_constants,
    forms as users_forms,
)


def register(request):
    form = users_forms.CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(reverse_lazy('users:login'))

    return render(
        request,
        users_constants.TEMPATE_REGISTER_PAGE,
        {'form': form}
    )
