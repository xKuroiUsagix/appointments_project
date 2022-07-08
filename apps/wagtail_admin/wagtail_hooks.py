from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)

from specialist_api.models import (
    Location,
    Service,
    Worker,
    WorkerService,
    Schedule,
    Appointment
)


class LocationAdmin(ModelAdmin):
    model = Location
    menu_label = 'Location'
    list_display = ('city', 'street', 'street_number', 'appartment_address')
    search_fields = ('city', 'street')


class ServiceAdmin(ModelAdmin):
    model = Service
    menu_label = 'Service'
    list_display = ('name', 'price', 'currency', 'length')
    search_fields = ('name',)


class WorkerAdmin(ModelAdmin):
    model = Worker
    menu_label = 'Worker'
    list_display = ('user',)
    search_fields = ('user',)


class WorkerServiceAdmin(ModelAdmin):
    model = WorkerService
    menu_label = 'Attach Services'
    list_display = ('worker', 'service')
    search_fields = ('worker', 'service')


class ScheduleAdmin(ModelAdmin):
    model = Schedule
    menu_label = 'Schedule'
    list_display = ('location', 'worker', 'day_of_week', '_start_time', '_end_time')
    search_fields = ('location', 'worker')


class AppointmentAdmin(ModelAdmin):
    model = Appointment
    menu_label = 'Appointment'
    list_display = ('worker', 'client', 'service', 'scheduled_for')


class Administartion(ModelAdminGroup):
    menu_label = 'Administration'
    menu_order = 000
    items = (LocationAdmin, ServiceAdmin, WorkerAdmin, WorkerServiceAdmin, ScheduleAdmin, AppointmentAdmin)

modeladmin_register(Administartion)
