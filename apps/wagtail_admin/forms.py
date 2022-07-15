import re
from datetime import timedelta

from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.widgets import AdminTimeInput

from django.forms import ValidationError
from django.apps import apps


class ServiceAdminForm(WagtailAdminModelForm):
    
    class Meta:
        widgets = {
            'duration': AdminTimeInput()
        }
    
    def clean(self):
        data = self.cleaned_data
        duration = data['duration']
        duration_str = str(duration)
        
        # pattern meaning:
        # select a string in format H:MM:SS
        pattern = r'^[0-9]:[0-9]{2}:[0-9]{2}$'
        if re.fullmatch(pattern, duration_str) is None:
            error_message = 'Bad duration format. Avaliable format: HH:MM'
            self.add_error('duration', error_message)
        
        # In this case, duration comes to the server
        # in format: `HH:MM`, but django's DurationField parses data
        # in format: `DD HH:MM:SS`, and because of it, our hours
        # go to database as minutes, and minutes go as seconds.
        #
        # So in case to fix it, hours must be set directly as hours
        # and minutes must be set directly as minutes.
        first_colon_id = duration_str.find(':')
        
        duration_str = duration_str[first_colon_id+1:]
        duration_hours = int(duration_str[:2])
        duration_minutes = int(duration_str[3:])
        
        data['duration'] = timedelta(hours=duration_hours, minutes=duration_minutes)
        
        return data


class ScheduleAdminForm(WagtailAdminModelForm):
    
    def clean(self):
        Schedule = apps.get_model('specialist_api', 'Schedule')
        data = self.cleaned_data

        try:
            Schedule.validate_timevalue(data['start_time'])
            Schedule.validate_timevalue(data['end_time'])
        except ValueError as e:
            raise ValidationError(e)
        
        if not Schedule.is_location_free(data['location'],
                                           data['day_of_week'],
                                           data['start_time'],
                                           data['end_time']):
            raise ValidationError('Location is not free at that time.')
        
        return data


class AppointmentAdminForm(WagtailAdminModelForm):
    
    def clean(self):
        Appointment = apps.get_model('specialist_api', 'Appointment')
        data = self.cleaned_data

        try:
            Appointment.is_apoointment_avaliable(data['worker'],
                                                data['scheduled_for'],
                                                data['service'])
        except ValueError as e:
            raise ValidationError(e.args)
        
        return data
