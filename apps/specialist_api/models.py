import calendar
from datetime import time, date

from django.db import models
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _

from appointments_project import settings
from wagtail_admin.forms import (
    ScheduleAdminForm, AppointmentAdminForm, ServiceAdminForm
)


User = settings.AUTH_USER_MODEL


class Location(models.Model):
    """
    Stores a single location entry.
    """
    city = models.CharField(max_length=128, db_index=True)
    street = models.CharField(max_length=128)
    street_number = models.CharField(max_length=64)
    appartment_address = models.CharField(max_length=64, null=True, blank=True)
    
    class Meta:
        db_table = 'location'
        ordering = ['city']
    
    def __str__(self):
        return f'{self.city}, {self.street}, {self.street_number}, {self.appartment_address}'


class Service(models.Model):
    """
    Stores a single service entry.
    """
    UNITED_STATES_DOLLAR = 'USD'
    EURO = 'EUR'
    GREATE_BRITAIN_POUND = 'GBP'
    JAPANESE_YEN = 'JPY'
    CHINESE_YUAN = 'CNY'
    UKRANIAN_HRYVNIA = 'UAH'
    CURRENCY_CHOICES = [
        (UNITED_STATES_DOLLAR, _('United States Dollar')),
        (EURO, _('Euro')),
        (GREATE_BRITAIN_POUND, _('Great Britain Pound')),
        (JAPANESE_YEN, _('Japanese Yen')),
        (CHINESE_YUAN, _('Chinese Yuan')),
        (UKRANIAN_HRYVNIA, _('Ukrainian Hryvnia'))
    ]
    name = models.CharField(max_length=128, unique=True, db_index=True)
    price = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    duration = models.DurationField()
    
    base_form_class = ServiceAdminForm
    
    class Meta:
        db_table = 'service'
    
    def __str__(self):
        return f'{self.name}'


class Worker(models.Model):
    """
    Stores a single worker entry, related to :model: `specialist_api.Service` through
    :model: `specialsit_api.WorkerService`, :model: `specialist_api.Location` through
    `specialist_api.Schedules` and :model: `specialist_api.User` as worker profile.
    """
    profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    services = models.ManyToManyField(Service, through='WorkerService', blank=True)
    schedules = models.ManyToManyField(Location, through='Schedule', blank=True)
    appointments = models.ManyToManyField(User, through='Appointment', blank=True)
    proffession = models.CharField(max_length=128)
    
    class Meta:
        db_table = 'worker'
    
    def __str__(self):
        return str(self.profile)
    
    def get_worker_schedule(self):
        """:returns: schedule of the worker."""
        return Schedule.objects.filter(worker=self)
    
    def get_worker_services(self):
        """:returns: services which worker provides."""
        return Service.objects.filter(worker=self)


class WorkerService(models.Model):
    """
    Stores relations between :model: `specialist_api.Worker` and
    :model: `specialist_api.Service`
    """
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'worker_service'


class Schedule(models.Model):
    """
    Stores a single day schedule, which related to :model: `specialsit_api.Worker` and
    :model: `specialist_api.Location`, where worker provides their services.
    """
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
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, db_index=True)
    day_of_week = models.SmallIntegerField(choices=DAYS_OF_WEEK_CHOICES, db_index=True)
    _start_time = models.TimeField(verbose_name='start time', name='start_time')
    _end_time = models.TimeField(verbose_name='end time', name='end_time')
    
    base_form_class = ScheduleAdminForm

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
        Validates given time value and :raise: ValueError if validation fails.
        :returns: True if exceptions haven't been raised.
        """
        if not isinstance(value, time):
            raise ValueError('value must be an instance of class time')
        if not (0 < value.hour < 24):
            raise ValueError('value must be between 0 and 24 hours')
        
        return True
    
    @staticmethod
    def is_location_free(location, day_of_week: int, start_time:time, end_time:time):
        """
        Method says is given location is free at given day_of_week at given
        start and end time.
        :returns: True if location is free, else False.
        """
        schedule_for_day = Schedule.objects.filter(
            location=location,
            day_of_week=day_of_week,
            start_time__lte=end_time,
            end_time__gte=start_time
        )
        return not bool(schedule_for_day)


class Appointment(models.Model):
    """
    Stores a single appointment for :model: `specialist_api.CustomUser`,
    related to :model: `specialist_api.Worker` and :model: `specialist_api.Service`.
    """
    client = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, db_index=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    scheduled_for = models.DateTimeField()
    
    base_form_class = AppointmentAdminForm
    
    class Meta:
        db_table = 'appointment'
        ordering = ['-scheduled_for']
    
    def __str__(self):
        return f'{self.client} appointed to {self.worker} on {self.scheduled_for} for {self.service} service duration.'
    
    def get_service_endtime(self):
        service_end = (datetime.combine(date.min, self.scheduled_for.time())
                       + self.service.duration)
        return service_end.time()
    
    @staticmethod
    def _has_free_place(worker, scheduled_for, service):
        """
        Method says is the worker has free space in their schedule
        to provide given service, depending on existing appointments.
        :returns: True if there is free space, else False.
        """
        appointments = Appointment.objects.filter(worker=worker, scheduled_for__date=scheduled_for.date())
        
        for appointment in appointments:
            current_service_start = appointment.scheduled_for.time()
            current_service_end = appointment.get_service_endtime()
            given_service_end = (datetime.combine(date.min, scheduled_for.time())
                                 + service.duration).time()
            
            # Checking if given appointment placed inside other existing appointment
            if (current_service_start <= scheduled_for.time() <= current_service_end or
                    current_service_start <= given_service_end <= current_service_end):
                return False
            # Checking if existing appointment placed inside given appointment
            if (scheduled_for.time() <= current_service_start and
                    given_service_end > current_service_start):
                return False

        return True
    
    @staticmethod
    def _is_in_schedule(worker, scheduled_for, service):
        """
        Method says is worker works at given datetime and is
        given service can be provided without overflowing from schedule.
        :returns: True if statements from earlier are statisfied, else False.
        
        This method doesn't check existing appointments.
        """
        schedules = Schedule.objects.filter(worker=worker, day_of_week=scheduled_for.weekday())
        service_end = datetime.combine(date.min, scheduled_for.time()) + service.duration
        
        for schedule in schedules:
            if (schedule.start_time <= scheduled_for.time() <= schedule.end_time and
                    service_end.time() <= schedule.end_time):
                return True
    
        return False
    
    @staticmethod
    def is_apoointment_avaliable(worker, scheduled_for, service):
        """
        Method says is the worker can provide given service at fiven date and time.
        :returns: True if appointment is avaliable, else False.
        """
        if not Appointment._is_in_schedule(worker, scheduled_for, service):
            raise ValueError("Given date and/or time not in worker's schedule.")

        if not Appointment._has_free_place(worker, scheduled_for, service):
            raise ValueError('Given date and/or time not free.')
        
        return True
