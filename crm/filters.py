import django_filters
from django_filters import FilterSet
from .models import Customer


class CustomerFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Customer
        fields = ['name', 'email']