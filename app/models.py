from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError



class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        return self.name
    
    def clean(self):
        if not (0 <= self.on_time_delivery_rate <= 100):
            raise ValidationError("On-Time Delivery Rate should be between 0 and 100.")
        if not (0 <= self.quality_rating_avg <= 5):  # Assuming quality rating is on a scale of 0 to 5
            raise ValidationError("Quality Rating Average should be between 0 and 5.")
        if self.average_response_time < 0:
            raise ValidationError("Average Response Time should not be negative.")
        if not (0 <= self.fulfillment_rate <= 100):
            raise ValidationError("Fulfillment Rate should be between 0 and 100.")


class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"PO-{self.po_number} for {self.vendor.name}"
    
    def clean(self):
        if not (0 <= self.on_time_delivery_rate <= 100):
            raise ValidationError("On-Time Delivery Rate should be between 0 and 100.")
        if not (0 <= self.quality_rating_avg <= 5):  # Assuming quality rating is on a scale of 0 to 5
            raise ValidationError("Quality Rating Average should be between 0 and 5.")
        if self.average_response_time < 0:
            raise ValidationError("Average Response Time should not be negative.")
        if not (0 <= self.fulfillment_rate <= 100):
            raise ValidationError("Fulfillment Rate should be between 0 and 100.")

    def update_vendor_performance(self):
        vendor = self.vendor
        completed_pos = PurchaseOrder.objects.filter(vendor=vendor, status='completed')

        # On-Time Delivery Rate
        completed_count = completed_pos.count()
        vendor.on_time_delivery_rate = (completed_pos.filter(delivery_date__lte=timezone.now()).count() / completed_count * 100) if completed_count > 0 else 0.0

        # Quality Rating Average
        quality_ratings = completed_pos.values_list('quality_rating', flat=True).exclude(quality_rating__isnull=True)
        vendor.quality_rating_avg = sum(quality_ratings) / len(quality_ratings) if quality_ratings else 0.0

        # Average Response Time
        acknowledgment_dates = completed_pos.values_list('acknowledgment_date', flat=True).exclude(acknowledgment_date__isnull=True)
        issue_dates = completed_pos.values_list('issue_date', flat=True)
        response_times = [ack_date - issue_date for ack_date, issue_date in zip(acknowledgment_dates, issue_dates)]
        vendor.average_response_time = sum(response_times, timedelta()) / len(response_times) if response_times else timedelta()

        # Fulfillment Rate
        fulfillment_count = completed_pos.filter(status='completed', quality_rating__isnull=True).count()
        vendor.fulfillment_rate = (fulfillment_count / completed_count * 100) if completed_count > 0 else 0.0

        vendor.save()

def update_vendor_metrics(sender, instance, **kwargs):
    instance.update_vendor_performance()
    
class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"Performance record for {self.vendor.name} on {self.date}"
    

