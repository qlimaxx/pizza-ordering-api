from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (Customer, CustomerInfo, Order,
                     Pizza, PizzaDetail, PizzaOrder)


CUSTOMER1 = {'name': 'Customer1', 'address': 'Address1', 'phone': '1234'}
CUSTOMER2 = {'name': 'Customer2', 'address': 'Address2', 'phone': '5678'}
PIZZA_DETAILS1 = {'size': 'Small', 'count': 3}
PIZZA_DETAILS2 = {'size': 'Large', 'count': 2}
PIZZA_NAME1 = 'Cheese'
PIZZA_NAME2 = 'Chicken'
NOT_FOUND_UUID = 'ffffffff-ffff-ffff-ffff-ffffffffffff'


class OrderTestCase(APITestCase):

    def _create_order(self, customer_index=1):
        CUSTOMER = CUSTOMER1 if customer_index == 1 else CUSTOMER2
        PIZZA_NAME = PIZZA_NAME1 if customer_index == 1 else PIZZA_NAME2
        customer = Customer.objects.create(name=CUSTOMER['name'])
        customer_info = CustomerInfo.objects.create(
            address=CUSTOMER['address'],
            phone=CUSTOMER['phone'],
            customer=customer)
        order = Order.objects.create(customer_info=customer_info)
        pizza = Pizza.objects.create(name=PIZZA_NAME)
        pizza_order = PizzaOrder.objects.create(order=order, pizza=pizza)
        PizzaDetail.objects.create(**PIZZA_DETAILS1, pizza_order=pizza_order)
        return order

    def test_list_orders(self):
        self._create_order()
        self._create_order(customer_index=2)
        response = self.client.get(reverse('api:orders-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = response.json()
        self.assertIsInstance(order_data, list)
        self.assertEqual(len(order_data), 2)

    def test_filter_list_orders(self):
        order1 = self._create_order()
        order2 = self._create_order(customer_index=2)
        order2.status = Order.DELIVERED_STATUS
        order2.save()
        self.assertEqual(Order.objects.count(), 2)
        response = self.client.get(
            reverse('api:orders-list'), {'status': Order.DELIVERED_STATUS})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = response.json()
        self.assertEqual(len(order_data), 1)
        self.assertEqual(order_data[0]['id'], str(order2.id))
        customer_id = str(order1.customer_info.customer.id)
        response = self.client.get(
            reverse('api:orders-list'), {'customer': customer_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = response.json()
        self.assertEqual(len(order_data), 1)
        self.assertEqual(order_data[0]['id'], str(order1.id))

    def test_create_order_success(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_data = response.json()
        order = Order.objects.first()
        customer = Customer.objects.first()
        customer_info = CustomerInfo.objects.first()
        pizza_order = PizzaOrder.objects.first()
        pizza_detail = PizzaDetail.objects.first()
        self.assertEqual(str(order.id), order_data['id'])
        self.assertEqual(order.customer_info, customer_info)
        self.assertEqual(str(customer.id), order_data['customer']['id'])
        self.assertEqual(customer.name, CUSTOMER1['name'])
        self.assertEqual(customer_info.address, CUSTOMER1['address'])
        self.assertEqual(customer_info.phone, CUSTOMER1['phone'])
        self.assertEqual(pizza_order.order, order)
        self.assertEqual(pizza_order.pizza, pizza)
        self.assertEqual(pizza_detail.pizza_order, pizza_order)
        self.assertEqual(pizza_detail.size, PIZZA_DETAILS1['size'])
        self.assertEqual(pizza_detail.count, PIZZA_DETAILS1['count'])

    def test_create_order_with_no_customer(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': {},
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_orders_with_existing_customer(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        Customer.objects.create(name=CUSTOMER1['name'])
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(CustomerInfo.objects.count(), 0)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(CustomerInfo.objects.count(), 1)

    def test_create_two_orders_with_same_customer(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(CustomerInfo.objects.count(), 1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(CustomerInfo.objects.count(), 1)

    def test_create_two_orders_with_two_customers(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(CustomerInfo.objects.count(), 1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER2,
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(CustomerInfo.objects.count(), 2)

    def test_create_order_with_no_pizzas(self):
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1, 'pizzas': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_not_found_pizza(self):
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{'id': NOT_FOUND_UUID, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_two_pizzas_with_same_id(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [
                {'id': pizza.id, 'details': [PIZZA_DETAILS1]},
                {'id': pizza.id, 'details': [PIZZA_DETAILS1]}
            ]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_without_details_in_pizza(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{'id': pizza.id, 'details': []}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_pizza_size_repeated_more_than_once(self):
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        response = self.client.post(reverse('api:orders-list'), {
            'customer': CUSTOMER1,
            'pizzas': [{
                'id': pizza.id,
                'details': [PIZZA_DETAILS1, PIZZA_DETAILS1]
            }]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_success(self):
        order = self._create_order()
        pizza = Pizza.objects.create(name=PIZZA_NAME2)
        response = self.client.put(reverse('api:orders-detail',
                                           args=(str(order.id),)), {
            'customer': CUSTOMER2,
            'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS2]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = response.json()
        order.refresh_from_db()
        pizza_detail = PizzaDetail.objects.first()
        pizza_order = order.pizzas.all()[0]
        pizza_detail = pizza_order.details.all()[0]
        self.assertEqual(str(order.id), order_data['id'])
        self.assertEqual(str(order.customer_info.customer.id),
                         order_data['customer']['id'])
        self.assertEqual(order.customer_info.customer.name, CUSTOMER2['name'])
        self.assertEqual(order.customer_info.address, CUSTOMER2['address'])
        self.assertEqual(order.customer_info.phone, CUSTOMER2['phone'])
        self.assertEqual(pizza_order.pizza, pizza)
        self.assertEqual(pizza_detail.size, PIZZA_DETAILS2['size'])
        self.assertEqual(pizza_detail.count, PIZZA_DETAILS2['count'])

    def test_update_order_with_existing_customer_name(self):
        order = self._create_order()
        self._create_order(customer_index=2)
        pizza_id = str(order.pizzas.first().pizza.id)
        response = self.client.put(reverse('api:orders-detail',
                                           args=(str(order.id),)), {
            'customer': CUSTOMER2,
            'pizzas': [{'id': pizza_id, 'details': [PIZZA_DETAILS1]}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_update_order_when_delivering_or_delivered(self):
        order = self._create_order()
        pizza = Pizza.objects.create(name=PIZZA_NAME2)
        for order_status in [Order.DELIVERING_STATUS, Order.DELIVERED_STATUS]:
            order.status = order_status
            order.save()
            response = self.client.put(reverse('api:orders-detail',
                                               args=(str(order.id),)), {
                'customer': CUSTOMER2,
                'pizzas': [{'id': pizza.id, 'details': [PIZZA_DETAILS2]}]
            }, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order_success(self):
        order = self._create_order()
        response = self.client.get(
            reverse('api:orders-detail', args=(str(order.id),)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_data = response.json()
        self.assertEqual(str(order.id), order_data['id'])

    def test_retrieve_order_not_found(self):
        response = self.client.get(
            reverse('api:orders-detail', args=(NOT_FOUND_UUID,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_success(self):
        order = self._create_order()
        response = self.client.delete(
            reverse('api:orders-detail', args=(str(order.id),)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(CustomerInfo.objects.count(), 1)
        self.assertEqual(Pizza.objects.count(), 1)
        self.assertEqual(PizzaOrder.objects.count(), 0)
        self.assertEqual(PizzaDetail.objects.count(), 0)

    def test_delete_order_not_found(self):
        response = self.client.delete(
            reverse('api:orders-detail', args=(NOT_FOUND_UUID,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderStatusTestCase(APITestCase):

    def _create_order(self):
        customer = Customer.objects.create(name=CUSTOMER1['name'])
        customer_info = CustomerInfo.objects.create(
            address=CUSTOMER1['address'],
            phone=CUSTOMER1['phone'],
            customer=customer)
        order = Order.objects.create(customer_info=customer_info)
        pizza = Pizza.objects.create(name=PIZZA_NAME1)
        pizza_order = PizzaOrder.objects.create(order=order, pizza=pizza)
        PizzaDetail.objects.create(**PIZZA_DETAILS1, pizza_order=pizza_order)
        return order

    def test_update_status_success(self):
        order = self._create_order()
        response = self.client.put(reverse('api:order-status',
                                           args=(str(order.id),)), {
            'status': Order.DELIVERING_STATUS
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.DELIVERING_STATUS)

    def test_update_status_to_delivered(self):
        order = self._create_order()
        self.assertFalse(order.delivered)
        self.assertIsNone(order.delivered_at)
        response = self.client.put(reverse('api:order-status',
                                           args=(str(order.id),)), {
            'status': Order.DELIVERED_STATUS
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.DELIVERED_STATUS)
        self.assertTrue(order.delivered)
        self.assertIsNotNone(order.delivered_at)

    def test_cannot_change_status_to_prior_status(self):
        order = self._create_order()
        order.status = Order.DELIVERING_STATUS
        order.save()
        response = self.client.put(reverse('api:order-status',
                                           args=(str(order.id),)), {
            'status': Order.PROCESSING_STATUS
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
