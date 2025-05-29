from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from api import views as api_views


schema_view = get_schema_view(
   openapi.Info(
      title="Barter API",
      default_version='v1',
      description="Документация API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'ads', api_views.AdViewSet, basename='ad')
router.register(
    r'proposals',
    api_views.ExchangeProposalViewSet,
    basename='proposal'
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'docs/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'auth/token/',
        TokenObtainPairView.as_view(),
        name='token-obtain-pair'),
    path(
        'auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token-refresh'
    ),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path(
        'auth/register/',
        UserViewSet.as_view({'post': 'create'}),
        name='user-register'
    ),
]

