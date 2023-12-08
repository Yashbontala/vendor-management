from django.test import TestCase

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from django.utils import timezone

class VendorAPITests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com')
        self.vendor = Vendor.objects.create(name='Test Vendor', contact_details='Contact Details', address='Test Address', vendor_code='123')

    def test_create_vendor(self):
        self.client.force_authenticate(user=self.superuser)
        url = '/api/vendors/'
        data = {'name': 'New Vendor', 'contact_details': 'New Contact', 'address': 'New Address', 'vendor_code': '456'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vendor.objects.count(), 2)
        self.assertEqual(Vendor.objects.last().name, 'New Vendor')

    def test_get_vendor_list(self):
        self.client.force_authenticate(user=self.superuser)
        url = '/api/vendors/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Vendor')

    def test_get_vendor_detail(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/vendors/{self.vendor.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Vendor')

    def test_update_vendor(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/vendors/{self.vendor.id}/'
        data = {'name': 'Updated Vendor', 'contact_details': 'Updated Contact', 'address': 'Updated Address', 'vendor_code': '789'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendor.objects.get(id=self.vendor.id).name, 'Updated Vendor')

    def test_delete_vendor(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/vendors/{self.vendor.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vendor.objects.count(), 0)

class PurchaseOrderAPITests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com')
        self.vendor = Vendor.objects.create(name='Test Vendor', contact_details='Contact Details', address='Test Address', vendor_code='123')
        self.purchase_order_data = {
            'po_number': 'PO123',
            'vendor': self.vendor.id,
            'order_date': timezone.now(),
            'delivery_date': timezone.now() + timezone.timedelta(days=5),
            'items': [{'name': 'Item1', 'quantity': 10}],
            'quantity': 10,
            'status': 'completed',
            'quality_rating': 4.5,
            'issue_date': timezone.now(),
            'acknowledgment_date': timezone.now()
        }
        self.purchase_order = PurchaseOrder.objects.create(**self.purchase_order_data)

    def test_create_purchase_order(self):
        self.client.force_authenticate(user=self.superuser)
        url = '/api/purchase_orders/'
        response = self.client.post(url, self.purchase_order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 2)
        self.assertEqual(PurchaseOrder.objects.last().po_number, 'PO123')

    def test_get_purchase_order_list(self):
        self.client.force_authenticate(user=self.superuser)
        url = '/api/purchase_orders/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['po_number'], 'PO123')

    def test_get_purchase_order_detail(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/purchase_orders/{self.purchase_order.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['po_number'], 'PO123')

    def test_update_purchase_order(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/purchase_orders/{self.purchase_order.id}/'
        data = {'po_number': 'PO456', 'status': 'pending'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PurchaseOrder.objects.get(id=self.purchase_order.id).po_number, 'PO456')

    def test_delete_purchase_order(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/purchase_orders/{self.purchase_order.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PurchaseOrder.objects.count(), 0)

class VendorPerformanceAPITests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com')
        self.vendor = Vendor.objects.create(name='Test Vendor', contact_details='Contact Details', address='Test Address', vendor_code='123')

    def test_get_vendor_performance(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/vendors/{self.vendor.id}/performance/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('on_time_delivery_rate', response.data)
        self.assertIn('quality_rating_avg', response.data)
        self.assertIn('average_response_time', response.data)
        self.assertIn('fulfillment_rate', response.data)

class AcknowledgePurchaseOrderAPITests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='admin', password='adminpassword', email='admin@example.com')
        self.vendor = Vendor.objects.create(name='Test Vendor', contact_details='Contact Details', address='Test Address', vendor_code='123')
        self.purchase_order_data = {
            'po_number': 'PO123',
            'vendor': self.vendor.id,
            'order_date': timezone.now(),
            'delivery_date': timezone.now() + timezone.timedelta(days=5),
            'items': [{'name': 'Item1', 'quantity': 10}],
            'quantity': 10,
            'status': 'completed',
            'quality_rating': 4.5,
            'issue_date': timezone.now(),
            'acknowledgment_date': None
        }
        self.purchase_order = PurchaseOrder.objects.create(**self.purchase_order_data)

    def test_acknowledge_purchase_order(self):
        self.client.force_authenticate(user=self.superuser)
        url = f'/api/purchase_orders/{self.purchase_order.id}/acknowledge/'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(PurchaseOrder.objects.get(id=self.purchase_order.id).acknowledgment_date)

