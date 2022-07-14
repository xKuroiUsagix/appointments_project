from wagtail.admin.forms import WagtailAdminModelForm

from django.forms import ValidationError
from django.apps import apps


class ScheduleAdminForm(WagtailAdminModelForm):
    def clean(self):
        Schedule = apps.get_model('specialist_api', 'Schedule')
        data = self.cleaned_data

        try:
            Schedule.validate_timevalue(data['_start_time'])
            Schedule.validate_timevalue(data['_end_time'])
        except ValueError as e:
            raise ValidationError(e)
        
        if not Schedule.is_location_free(data['location'],
                                           data['day_of_week'],
                                           data['_start_time'],
                                           data['_end_time']):
            raise ValidationError('Location is not free at that time.')
        
        return data


class AppointmentAdminForm(WagtailAdminModelForm):
    def clean(self):
        Appointment = apps.get_model('specialist_api', 'Appointment')
        data = self.cleaned_data
        
        if not Appointment.is_apoointment_avaliable(data['worker'],
                                                   data['scheduled_for'],
                                                   data['service']):
            raise ValidationError('Appointment is not avaliable at that time.')
        
        return data
