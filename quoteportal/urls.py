from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^portal/', include('portal.urls'))
]

admin.site.site_header = "Technical Services Requests Portal"
admin.site.site_title = "Requests Admin"
