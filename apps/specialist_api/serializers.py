from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from django.utils import timezone

from .models import (
    Location, Service, Worker, Schedule, Appointment
)
from client_api.serializers import UserSerializer


class LocationSerializer(ModelSerializer):
    
    class Meta:
        model = Location
        fields = '__all__'


class ServiceSerializer(ModelSerializer):
        
    class Meta:
        model = Service
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


class WorkerSerializer(ModelSerializer):
    schedules = ScheduleSerializer(source='get_worker_schedule', many=True)
    services = ServiceSerializer(source='get_worker_services', many=True)
    profile = UserSerializer()
    
    class Meta:
        model = Worker
        fields = ['profile', 'services', 'schedules', 'proffession']


class AppointmentSerializer(ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'worker', 'client', 'scheduled_for', 'service']
    
    def validate(self, data):
        data_copy = data.copy()
        worker_profile_id = self.context.get('worker_profile_id')
        
        if self.instance is not None:
            data_copy['worker'] = self.instance.worker
            data_copy['client'] = self.instance.client
            data_copy['service'] = self.instance.service
        
        if data_copy['scheduled_for'] <= timezone.now():
            raise serializers.ValidationError('Date and Time must be in future.')
        
        if data_copy['client'].id == worker_profile_id:
            raise serializers.ValidationError("You can't make an appointment to yourself!")
        
        try:
            Appointment.is_apoointment_avaliable(data_copy['worker'],
                                                 data_copy['scheduled_for'],
                                                 data_copy['service'])
        except ValueError as e:
            raise serializers.ValidationError(e.args)
        
        return data_copy
    