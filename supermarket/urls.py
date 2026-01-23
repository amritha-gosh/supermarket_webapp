from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop.admin import my_admin_site, wigan_admin, southport_admin

urlpatterns = [
    path('admin/',         my_admin_site.urls),
    path('admin/wigan/',   wigan_admin.urls),
    path('admin/southport/', southport_admin.urls),

    path('accounts/', include('allauth.urls')),
    path('', include('shop.urls')),
    path('api/', include('shop.api_urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
