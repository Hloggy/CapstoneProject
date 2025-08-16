from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import User, InventoryItem, Category

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = APIClient()
    
    def test_user_registration(self):
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
    
    def test_user_login(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class InventoryItemTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items',
            created_by=self.user
        )
        self.item = InventoryItem.objects.create(
            name='Laptop',
            description='High performance laptop',
            quantity=10,
            price=999.99,
            category=self.category,
            created_by=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_inventory_item(self):
        url = reverse('item-list')
        data = {
            'name': 'Smartphone',
            'description': 'Latest smartphone',
            'quantity': 20,
            'price': 699.99,
            'category_id': self.category.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryItem.objects.count(), 2)
    
    def test_retrieve_inventory_item(self):
        url = reverse('item-detail', args=[self.item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')
    
    def test_update_inventory_item(self):
        url = reverse('item-detail', args=[self.item.id])
        data = {
            'name': 'Laptop Pro',
            'quantity': 15,
            'price': 1099.99
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Laptop Pro')
        self.assertEqual(self.item.quantity, 15)
    
    def test_delete_inventory_item(self):
        url = reverse('item-detail', args=[self.item.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InventoryItem.objects.count(), 0)
    
    def test_adjust_stock(self):
        url = reverse('item-adjust-stock', args=[self.item.id])
        data = {
            'change': -5,
            'notes': 'Sold 5 units'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 5)

class PermissionTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic items',
            created_by=self.user1
        )
        self.item = InventoryItem.objects.create(
            name='Laptop',
            description='High performance laptop',
            quantity=10,
            price=999.99,
            category=self.category,
            created_by=self.user1
        )
        self.client = APIClient()
    
    def test_user_cannot_access_others_items(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('item-detail', args=[self.item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_can_access_all_items(self):
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=admin)
        url = reverse('item-detail', args=[self.item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

