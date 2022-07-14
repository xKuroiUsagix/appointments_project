from wagtail.admin import urls as wagtailadmin_urls

from django.urls import path, include


urlpatterns = [
    path('cms/', include(wagtailadmin_urls))
]