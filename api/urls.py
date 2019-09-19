from django.urls import path
from rest_framework import routers

from . import views


app_name = 'api'

router = routers.SimpleRouter()
router.register(r'orders', views.OrderViewSet, basename='orders')
router.register(r'pizzas', views.PizzaViewSet, basename='pizzas')

urlpatterns = router.urls + [
    path('orders/<uuid:pk>/status/',
         views.OrderStatusView.as_view(), name='order-status')
]
