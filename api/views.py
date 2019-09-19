from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response

from .filters import OrderFilter
from .models import Customer, CustomerInfo, Order, Pizza
from .serializers import (OrderSerializer, OrderStatusSerializer,
                          PizzaSerializer)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer_info__customer').prefetch_related(
        'pizzas__pizza').prefetch_related('pizzas__details')
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter

    def partial_update(self, request, pk):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OrderStatusView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializer


class PizzaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer
