from django.urls import path
from .views import OrderCreateAPIView, OrderListAPIView, OrderDetailAPIView, OrderCancelAPIView


app_name = 'orders'

urlpatterns = [
   path('', OrderListAPIView.as_view(), name='order-list'),
   path('checkout/', OrderCreateAPIView.as_view(), name='order-checkout'),
   path('<int:pk>/',OrderDetailAPIView.as_view(), name='order-detail' ),
   path('<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel')
   
]

