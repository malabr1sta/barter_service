from django.contrib.auth import views as auth_views
from django.urls import path
from users import (
    constants as users_constants,
    views as users_views,
)


app_name = "users"


urlpatterns = [
    path('register/', users_views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name=users_constants.TEMPATE_LOGIN_PAGE
        ),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
]

