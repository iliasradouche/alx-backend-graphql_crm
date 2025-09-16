from django.shortcuts import render
from django.http import JsonResponse
from .models import Customer, Order


def customer_list(request):
    """API view to list all customers"""
    customers = Customer.objects.all().values(
        'id', 'first_name', 'last_name', 'email', 'phone', 'is_active'
    )
    return JsonResponse(list(customers), safe=False)


def order_list(request):
    """API view to list all orders"""
    orders = Order.objects.select_related('customer').all().values(
        'id', 'order_number', 'total_amount', 'status',
        'customer__first_name', 'customer__last_name', 'created_at'
    )
    return JsonResponse(list(orders), safe=False)