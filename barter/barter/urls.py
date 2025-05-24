from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'


urlpatterns = [
    path('ads/', include('ads.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls'))
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
