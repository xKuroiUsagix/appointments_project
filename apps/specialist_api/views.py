from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from django.utils.timezone import datetime
from django.shortcuts import get_object_or_404

from .permissions import IsWorkerOrAdmin
from .serializers import AppointmentSerializer
from .models import Appointment, Worker


class AppointmentListAPIVIew(APIView):
    """
    get:
    Returns a list of all appointments for specific worker
    """
    permission_classes = [IsWorkerOrAdmin]
    model = Appointment
    serializer_class = AppointmentSerializer
    
    def get(self, request, worker_id, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset(worker_id))
        except ValueError as e:
            content = {'query params': e.args[0]}
            return Response(content, status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(queryset, many=True)
        
        for item, obj in zip(serializer.data, queryset):
            item['end_time'] = obj.get_service_endtime()
        
        return Response(serializer.data)
    
    def get_queryset(self, worker_id):
        worker = get_object_or_404(Worker, id=worker_id)
        return self.model.objects.filter(worker=worker)
    
    def filter_queryset(self, queryset):
        """
        Returns new queryset based on given filter params.
        
        All possible params:
            - specific_date (date): a date in format `dd-mm-yyyy`
            - lower_date (date): a bottom bound of date filter
            - upper_date (date): a top bound of date filter
        """
        DATE_FORMAT = '%d-%m-%Y'
        
        specific_date = self.request.query_params.get('specific_date')
        lower_date = self.request.query_params.get('lower_date')
        upper_date = self.request.query_params.get('upper_date')
        
        if (specific_date is None) and (lower_date is None) and (upper_date is None):
            return queryset
        
        # Filtering queryset by given date
        if specific_date is not None:
            specific_date = datetime.strptime(specific_date, DATE_FORMAT)
            return queryset.filter(scheduled_for__date=specific_date)
        
        if (lower_date is not None) and (upper_date is None):
            lower_date = datetime.strptime(lower_date, DATE_FORMAT)
            return queryset.filter(scheduled_for__date__gte=lower_date)
        
        if (upper_date is not None) and (lower_date is None):
            upper_date = datetime.strptime(upper_date, DATE_FORMAT)
            return queryset.filter(scheduled_for__date__lte=upper_date)
        
        lower_date = datetime.strptime(lower_date, DATE_FORMAT)
        upper_date = datetime.strptime(upper_date, DATE_FORMAT)
        
        return queryset.filter(scheduled_for__date__gte=lower_date,
                               scheduled_for__date__lte=upper_date)
