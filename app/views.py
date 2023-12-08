from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg
from django.utils import timezone
from .decorators import superuser_required


class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class PurchaseOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class VendorPerformanceView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = HistoricalPerformanceSerializer

    def retrieve(self, request, *args, **kwargs):
        vendor = self.get_object()
        performance_data = self.calculate_vendor_performance(vendor)
        serializer = self.get_serializer(performance_data)
        return Response(serializer.data)

    def calculate_vendor_performance(self, vendor):
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        
        on_time_delivery_rate = completed_pos.filter(delivery_date__lte=timezone.now()).count() / completed_pos.count() * 100 if completed_pos.count() > 0 else 0.0
        quality_rating_avg = completed_pos.aggregate(Avg('quality_rating'))['quality_rating__avg'] if completed_pos.filter(quality_rating__isnull=False).exists() else 0.0
        average_response_time = completed_pos.filter(acknowledgment_date__isnull=False).aggregate(Avg('acknowledgment_date' - 'issue_date'))['acknowledgment_date__avg'] if completed_pos.filter(acknowledgment_date__isnull=False).exists() else 0.0
        fulfillment_rate = completed_pos.filter(status='completed', quality_rating__isnull=True).count() / completed_pos.count() * 100 if completed_pos.count() > 0 else 0.0

        return {
            'on_time_delivery_rate': on_time_delivery_rate,
            'quality_rating_avg': quality_rating_avg,
            'average_response_time': average_response_time,
            'fulfillment_rate': fulfillment_rate
        }

class AcknowledgePurchaseOrderView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def perform_update(self, serializer):
        serializer.save(acknowledgment_date=timezone.now())
        vendor = serializer.instance.vendor
        vendor.update_vendor_performance()