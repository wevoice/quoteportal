from django.conf.urls import url, include
from django.contrib import admin
from ajax_select import urls as ajax_select_urls
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^portal/', include('portal.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Self-service Quote Portal"
admin.site.site_title = "Quote Admin"
admin.site.site_url = None
