import calendar
from datetime import timedelta, time

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    Worker, Location, Schedule, Service, Appointment
)


User = get_user_model()


class ScheduleModelTests(TestCase):
    """
    Provides tests for :model: `specialist_api.Schedule`
    """
    def setUp(self):
        user = User.objects.create_user(
            username='username',
            email='testmail@mail.com',
            password='testpass1',
            first_name='name',
            last_name='surname'
        )
        self.worker = Worker.objects.create(profile=user)
        self.location = Location.objects.create(
            city='City',
            street='Street',
            street_number='100',
            appartment_address='10'
        )
        self.start_hours = 6
        self.start_minutes = 30
        self.end_hours = 17
        self.end_minutes = 30
        self.day_of_week = calendar.MONDAY
        
        Schedule.objects.create(
            worker=self.worker,
            location=self.location,
            day_of_week=self.day_of_week,
            start_time=time(self.start_hours, self.start_minutes),
            end_time=time(self.end_hours, self.end_minutes)
        )
    
    def test_is_location_free(self):
        good_time_1 = [
            time(self.end_hours + 1),
            time(self.end_hours + 3)
        ]
        good_time_2 = [
            time(self.start_hours - 3),
            time(self.start_hours - 1)
        ]
        bad_time_1 = [
            time(self.start_hours + 1),
            time(self.start_hours + 2)
        ]
        bad_time_2 = [
            time(self.start_hours - 1),
            time(self.end_hours + 1)
        ]
        
        self.assertTrue(
            Schedule.is_location_free(
                location=self.location,
                day_of_week=self.day_of_week,
                start_time=good_time_1[0],
                end_time=good_time_1[1]
            )
        )
        self.assertTrue(
            Schedule.is_location_free(
                location=self.location,
                day_of_week=self.day_of_week,
                start_time=good_time_2[0],
                end_time=good_time_2[1]
            )
        )
        self.assertFalse(
            Schedule.is_location_free(
                location=self.location,
                day_of_week=self.day_of_week,
                start_time=bad_time_1[0],
                end_time=bad_time_1[1]
            )
        )
        self.assertFalse(
            Schedule.is_location_free(
                location=self.location,
                day_of_week=self.day_of_week,
                start_time=bad_time_2[0],
                end_time=bad_time_2[1]
            )
        )


class AppointmentModelTests(TestCase):
    """
    Provides tests for :model: `specialist_api.Appointment`.
    """
    def setUp(self):
        self.client = User.objects.create_user(
            username='username1',
            email='testmail1@mail.com',
            password='testpass1',
            first_name='client_name',
            last_name='client_surname'
        )
        worker_user = User.objects.create_user(
            username='username2',
            email='testmail2@mail.com',
            password='testpass2',
            first_name='worker_name',
            last_name='worker_surname'
        )
        
        self.worker = Worker.objects.create(profile=worker_user)
        
        service_length = timedelta(minutes=40)
        self.service = Service.objects.create(
            name='service_name',
            price=120,
            currency='USD',
            length=service_length
        )
        self.worker.services.add(self.service)
        
        
        location = Location.objects.create(
            city='City',
            street='Street',
            street_number='100',
            appartment_address='10'
        )
        self.start_time = time(8)
        self.end_time = time(16)
        
        self.schedule = Schedule.objects.create(
            location=location,
            worker=self.worker,
            day_of_week=calendar.MONDAY,
            start_time=self.start_time,
            end_time=self.end_time
        )
    
    def test_is_appointment_avaliable(self):
        year = 2022
        month = 7
        day = 4
        
        time_inside_schedule = timezone.datetime(year, month, day, self.start_time.hour)
        time_outside_schedule = timezone.datetime(year, month, day, self.start_time.hour - 1)

        self.assertIs(
            Appointment.is_apoointment_avaliable(
                worker=self.worker,
                service=self.service,
                scheduled_for=time_inside_schedule
            ),
            True
        )
        self.assertIs(
            Appointment.is_apoointment_avaliable(
                worker=self.worker,
                service=self.service,
                scheduled_for=time_outside_schedule
            ),
            False
        )
        
        # testing when there is appointment already
        Appointment.objects.create(
            client=self.client,
            worker=self.worker,
            service=self.service,
            scheduled_for=time_inside_schedule
        )
        
        self.assertIs(
            Appointment.is_apoointment_avaliable(
                worker=self.worker,
                service=self.service,
                scheduled_for=time_inside_schedule
            ),
            False
        )
        
    
