from django.db import models
from django.forms import ValidationError
from django.utils.timezone import datetime
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

import calendar
from datetime import timedelta, time, date

from wagtail.admin.forms import WagtailAdminModelForm
from client_api.models import Client


User = get_user_model()


class ScheduleAdminForm(WagtailAdminModelForm):
    def clean(self):
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
        data = self.cleaned_data
        
        if not Appointment.is_apoointment_avaliable(data['worker'],
                                                    data['scheduled_for'],
                                                    data['service']):
            raise ValidationError('Appointment is not avaliable at that time.')
        
        return data


class Location(models.Model):
    """
    A model for storing data about location.
    """
    city = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street_number = models.CharField(max_length=64)
    appartment_address = models.CharField(max_length=64, null=True, blank=True)
    
    class Meta:
        db_table = 'location'
    
    def __str__(self):
        return f'{self.city}, {self.street}, {self.street_number}, {self.appartment_address}'


class Service(models.Model):
    """
    A model for storing data about services which Worker can provide.
    """
    CURRENCY_CHOICES = (
        ('USD', _('United States Dollar')),
        ('EUR', _('Euro')),
        ('GBP', _('Great Britain Pound')),
        ('JPY', _('Japanese Yen')),
        ('CNY', _('Chinese Yuan')),
        ('UAH', _('Ukrainian Hryvnia'))
    )
    name = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    _seconds_length = models.FloatField(verbose_name='length')
    
    class Meta:
        db_table = 'service'
    
    def __str__(self):
        return f'{self.name}'
    
    @property
    def length(self):
        return self._seconds_length
    
    @length.getter
    def length(self):
        return timedelta(seconds=self._seconds_length)
    
    @length.setter
    def length(self, value:timedelta):
        """
        A setter which converts given timedelta value to seconds.
        """
        self._seconds_length = value.total_seconds()


class Worker(models.Model):
    """
    A model for storing data about worker.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker')
    work_schedule = models.ManyToManyField(Location, through='Schedule')
    services = models.ManyToManyField(Service, through='WorkerService')
    appointments = models.ManyToManyField(Client, through='Appointment')
    
    class Meta:
        db_table = 'worker'
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class WorkerService(models.Model):
    """
    A model for storing data about workers and services which they can provide.
    """
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'worker_service'


class Schedule(models.Model):
    """
    A model for storing data about worker's schedule for concrete day of week
    """
    base_form_class = ScheduleAdminForm
    DAYS_OF_WEEK_CHOICES = (
        (calendar.MONDAY, _('Monday')),
        (calendar.TUESDAY, _('Tuesday')),
        (calendar.WEDNESDAY, _('Wednesday')),
        (calendar.THURSDAY, _('Thursday')),
        (calendar.FRIDAY, _('Friday')),
        (calendar.SATURDAY, _('Saturday')),
        (calendar.SUNDAY, _('Sunday'))
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    day_of_week = models.SmallIntegerField(choices=DAYS_OF_WEEK_CHOICES)
    _start_time = models.TimeField(verbose_name='start time')
    _end_time = models.TimeField(verbose_name='end time')

    class Meta:
        db_table = 'schedule'
    
    def __str__(self):
        return f'{self.location}: {self.worker} | {self.day_of_week} | {self.start_time} - {self.end_time}'
    
    @property
    def start_time(self):
        return self._start_time
    
    @start_time.setter
    def start_time(self, value:time):
        self.validate_timevalue(value)
        self._start_time = value
    
    @property
    def end_time(self):
        return self._end_time
    
    @end_time.setter
    def end_time(self, value):
        self.validate_timevalue(value)
        self._end_time = value

    @staticmethod
    def validate_timevalue(value:time):
        """
        A method for time setters validation.
        This method checks if an instance of given value is time...
        if first check is True, then checks if given value represents...
        not more than 24 hours.
        Raises ValueError if any check is failed.
        """
        if not isinstance(value, time):
            raise ValueError('value must be an instance of class time')
        if not (0 < value.hour < 24):
            raise ValueError('value must be between 0 and 24 hours')
    
    @staticmethod
    def is_location_free(location, day_of_week, start_time:time, end_time:time):
        """
        A method for comparing given period of time (start_time, end_time) 
        for concrete day of a week with existing schedule.
        
        Returns: True if given period doesn't intersect with any other, else False.
        """
        schedule_for_day = Schedule.objects.filter(
            location=location,
            day_of_week=day_of_week,
            _start_time__lte=end_time,
            _end_time__gte=start_time
        )
        return not bool(schedule_for_day)


class Appointment(models.Model):
    """
    A model for sotring data about clients appointments.
    """
    base_form_class = AppointmentAdminForm
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    scheduled_for = models.DateTimeField()
    
    class Meta:
        db_table = 'appointment'
    
    def __str__(self):
        return f'{self.client} appointed to {self.worker} on {self.scheduled_for} for {self.service} service length.'
    
    @staticmethod
    def _is_worker_avaliable(worker, scheduled_for, service):
        """
        A static method for checking if a worker can provide given service for a client at given time.
        """
        appointments = Appointment.objects.filter(worker=worker)
        
        for appointment in appointments:
            current_service_start = appointment.scheduled_for
            current_service_end = (datetime.combine(date.min, appointment.scheduled_for.time())
                                   + appointment.service.length)
            given_service_end = (datetime.combine(date.min, scheduled_for.time())
                                 + service.length)

            # Checking if given appointment placed inside other existing appointment
            if (current_service_start.time() <= scheduled_for.time() <= current_service_end.time() or
                    current_service_start <= given_service_end <= current_service_end):
                return False
            # Checking if existing appointment placed inside given appointment
            if (scheduled_for.time() <= current_service_start and
                    given_service_end > current_service_start):
                return False
        return True
    
    @staticmethod
    def is_apoointment_avaliable(worker, scheduled_for, service):
        """
        A method for checking if client's appointment is avaliable.
        """
        schedules = Schedule.objects.filter(worker=worker, day_of_week=scheduled_for.weekday())
        service_end = (datetime.combine(date.min, scheduled_for.time())
                       + service.length)
        
        for schedule in schedules:
            # Checking if scheduled_for and service_end inside worker's schedule
            if (schedule.start_time <= scheduled_for.time() <= schedule.end_time and
                    service_end.time() <= schedule.end_time):
                return Appointment._is_worker_avaliable(worker, scheduled_for, service)
        return False
