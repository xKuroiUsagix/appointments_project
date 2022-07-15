from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)

from specialist_api.models import (
    Location, Service, Worker,
    Schedule, Appointment
)


class LocationAdmin(ModelAdmin):
    model = Location
    menu_label = 'Location'
    list_display = ('city', 'street', 'street_number', 'appartment_address')
    search_fields = ('city', 'street')


class ServiceAdmin(ModelAdmin):
    model = Service
    menu_label = 'Service'
    list_display = ('name', 'price', 'currency', 'duration')
    search_fields = ('name',)


class WorkerAdmin(ModelAdmin):
    model = Worker
    form_fields_exclude = ('appointments', 'schedules')
    menu_label = 'Worker'
    list_display = ('profile',)
    search_fields = ('profile',)


class ScheduleAdmin(ModelAdmin):
    model = Schedule
    menu_label = 'Schedule'
    list_display = ('location', 'worker', 'day_of_week', 'start_time', 'end_time')
    search_fields = ('location', 'worker')


class AppointmentAdmin(ModelAdmin):
    model = Appointment
    menu_label = 'Appointment'
    list_display = ('worker', 'client', 'service', 'scheduled_for')


class Administartion(ModelAdminGroup):
    menu_label = 'Administration'
    menu_order = 000
    items = (LocationAdmin, ServiceAdmin, WorkerAdmin, 
             ScheduleAdmin, AppointmentAdmin)

modeladmin_register(Administartion)
