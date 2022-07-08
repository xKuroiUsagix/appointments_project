from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import (
    Location,
    Service,
    Worker,
    WorkerService,
    Schedule,
    Appointment
)


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class ServiceSerializer(ModelSerializer):
    _seconds_length = serializers.TimeField()
    
    class Meta:
        model = Service
        fields = '__all__'
        

class WorkerSerializer(ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'


class ScheduleSerializer(ModelSerializer):    
    class Meta:
        model = Schedule
        fields = '__all__'
        
    def validate(self, data):
        try:
            self.model.validate_timevalue(data['start_time'])
            self.model.validate_timevalue(data['end_time'])
        except ValueError as e:
            raise serializers.ValidationError(e)
        if (self.model.is_location_free(data['location'],
                                        data['day_of_week'],
                                        data['start_time'],
                                        data['end_time'])):
            raise serializers.ValidationError('The given location is not free at that time.')
        return data


class AppointmentSerializer(ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        
    def validate(self, data):
        if (self.model.is_appointment_avaliable(data['worker'],
                                                data['scheduled_for'],
                                                data['service'])):
            raise serializers.ValidationError('An appointment is not avaliable at that date and/or time.')
        return data
    