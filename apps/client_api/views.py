from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from django.utils.timezone import datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from specialist_api.models import (
    Worker, Appointment, Service
)
from specialist_api.serializers import (
    WorkerSerializer, AppointmentSerializer
)
from .serializers import RegisterSerializer


User = get_user_model()
DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'


class RegisterAPIView(CreateAPIView):
    """
    Creates a new user.
    """
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class WorkerListAPIView(APIView):
    """
    get:
    Returns a list of all workers, which can be filtered by
    specific_date, proffession and/or service_name.
    """
    permission_classes = [AllowAny]
    model = Worker
    serializer_class = WorkerSerializer
    
    def get(self, request, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except ValueError as e:
            content = {'date': e.args[0]}
            return Response(content, status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(queryset, many=True)
        
        return Response(serializer.data)
    
    def get_queryset(self):
        return Worker.objects.all()
            
    def filter_queryset(self, queryset):
        """
        Returns new queryset based on given filter params.
        
        All possible params:
            - date (date): a date in format `dd-mm-yyyy`
            - proffession (str): a worker's proffession
        """
        DATE_FORMAT = '%d-%m-%Y'
        
        filtered_queryset = queryset
        filter_date =  self.request.query_params.get('date')
        proffession = self.request.query_params.get('proffession')
        weekday = datetime.strptime(filter_date, DATE_FORMAT).weekday() if filter_date else None
        
        if (weekday is None) and (proffession is None):
            return queryset
        
        if proffession is not None:
            filtered_queryset = self.filter_by_proffession(filtered_queryset, proffession)
        if weekday is not None:
            filtered_queryset = self.filter_by_weekday(filtered_queryset, weekday)
        
        return filtered_queryset
    
    def filter_by_weekday(self, queryset, weekday):
        filtered_queryset = []
        
        for worker in queryset:
            schedule = worker.get_worker_schedule()
            
            for record in schedule:
                if record.day_of_week == weekday:
                    filtered_queryset.append(worker)
                    break
        
        return filtered_queryset
    
    def filter_by_proffession(self, queryset, proffession):
        return queryset.filter(proffession__iexact=proffession)

class AppointmentCreateAPIView(APIView):
    """
    post:
    Creates a new appointment instance for current authenticated user
    to given worker.
    """
    permission_classes = [IsAuthenticated]
    model = Appointment
    serializer_class = AppointmentSerializer
    
    def post(self, request, worker_id):
        context = {
            'worker_profile_id': get_object_or_404(Worker, id=worker_id).profile.id
        }
        
        data = request.data.copy()
        data['worker'] = worker_id
        data['client'] = request.user.id
        data['scheduled_for'] = datetime.strptime(data['scheduled_for'], DATETIME_FORMAT)
        
        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AppointmentListAPIView(APIView):
    """
    get:
    Return a list of all appointments for current authenticated user.
    """
    permission_classes = [IsAuthenticated]
    model = Appointment
    serializer_class = AppointmentSerializer
    
    def get(self, request):
        appointments = self.get_queryset()
        serializer = self.serializer_class(appointments, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        return self.model.objects.filter(client=self.request.user)


class AppointmentDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    retrieve:
    Return an appointment details.
    
    update:
    Update an appointment instace.
    
    destroy:
    Delete an appointment
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']
    lookup_url_kwarg = 'appointment_id'
    model = Appointment
    serializer_class = AppointmentSerializer
    
    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        scheduled_for = data.get('scheduled_for')
        instance = self.get_object()
        
        data['client'] = instance.client.id
        data['worker'] = instance.worker.id
        
        try:
            if scheduled_for is not None:
                data['scheduled_for'] = datetime.strptime(scheduled_for, DATETIME_FORMAT)
            if data.get('service'):
                service = Service.objects.get(id=int(data['service']))
                if not service.worker_set.filter(id=instance.worker.id):
                    content = {'worker': 'This worker doesn\'t provide given service'}
                    return Response(content, status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response(e.args, status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            content = {
                'service': 'Given service does not exist'
            }
            return Response(content, status.HTTP_400_BAD_REQUEST)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    
    def get_queryset(self):
        return self.model.objects.filter(client=self.request.user)
    
    def get_object(self):
        appointment_id = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(self.get_queryset(), id=appointment_id)
