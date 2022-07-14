from django.urls import path

from .views import (
    RegisterAPIView, WorkerListAPIView, AppointmentCreateAPIView, 
    AppointmentListAPIView, AppointmentDetailAPIView
)


app_name = 'client_api'
urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('workers/', WorkerListAPIView.as_view(), name='workers'),
    path('appointment/worker/<int:worker_id>/', AppointmentCreateAPIView.as_view(), name='appointment_create'),
    path('appointment/<int:appointment_id>/', AppointmentDetailAPIView.as_view(), name='appointment_detail'),
    path('appointments/', AppointmentListAPIView.as_view(), name='appointments'),
]

