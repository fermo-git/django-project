from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Product


class CategoryTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(
			username='test_user',
			password='test_password123',
		)
		self.client.force_authenticate(user=self.user)
		self.category = Category.objects.create(name='Electronica')

	def test_create_category(self):
		response = self.client.post(
			'/api/categories/',
			{'name': 'Ropa'},
			format='json',
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Category.objects.count(), 2)

	def test_list_categories(self):
		response = self.client.get('/api/categories/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['name'], 'Electronica')


class ProductTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(
			username='test_user',
			password='test_password123',
		)
		self.client.force_authenticate(user=self.user)
		self.category = Category.objects.create(name='Electronica')
		self.product = Product.objects.create(
			name='Laptop',
			category=self.category,
			description='Laptop HP',
			price='15000.00',
		)

	def test_create_product(self):
		response = self.client.post(
			'/api/products/',
			{
				'name': 'Mouse',
				'category': self.category.id,
				'description': 'Mouse inalambrico',
				'price': '500.00',
				'is_active': True,
			},
			format='json',
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(Product.objects.count(), 2)

	def test_list_products(self):
		response = self.client.get('/api/products/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['name'], 'Laptop')

	def test_update_product(self):
		response = self.client.put(
			f'/api/products/{self.product.id}/',
			{
				'name': 'Laptop Pro',
				'category': self.category.id,
				'description': 'Laptop HP actualizada',
				'price': '18000.00',
				'is_active': True,
			},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		self.product.refresh_from_db()
		self.assertEqual(self.product.name, 'Laptop Pro')
		self.assertEqual(self.product.price, Decimal('18000.00'))

	def test_delete_product(self):
		response = self.client.delete(f'/api/products/{self.product.id}/')

		self.assertEqual(response.status_code, 204)
		self.assertEqual(Product.objects.count(), 0)


class ProductPatternTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = User.objects.create_user(
			username='patterns_user',
			password='test_password123',
		)
		self.client.force_authenticate(user=self.user)

	def test_factory_creates_product_with_default_category(self):
		product = Product.crear_con_categoria_default(
			name='Producto general',
			description='Producto sin categoria especifica',
			price=Decimal('250.00'),
		)

		self.assertEqual(product.category.name, 'General')
		self.assertEqual(Product.objects.count(), 1)

	def test_final_price_endpoint_uses_category_discount_strategy(self):
		electronics = Category.objects.create(name='Electronica')
		clothing = Category.objects.create(name='Ropa')
		Product.objects.create(
			name='Audifonos',
			category=electronics,
			description='Audifonos Bluetooth',
			price=Decimal('100.00'),
		)
		Product.objects.create(
			name='Camisa',
			category=clothing,
			description='Camisa de algodon',
			price=Decimal('100.00'),
		)

		response = self.client.get('/api/precio-final/')

		self.assertEqual(response.status_code, 200)
		prices = {item['name']: item for item in response.data}
		self.assertEqual(prices['Audifonos']['final_price'], Decimal('90.00'))
		self.assertEqual(prices['Camisa']['final_price'], Decimal('85.00'))
