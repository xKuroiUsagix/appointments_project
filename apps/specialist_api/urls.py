from django.urls import path

from .views import AppointmentListAPIVIew


app_name = 'specialist_api'
urlpatterns = [
    path('<int:worker_id>/appointments/', AppointmentListAPIVIew.as_view(), name='appointment_list'),
    # path('<int:worker_id>/appointment/<int:appointment_id>/'),
]
