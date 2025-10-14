from django.urls import path
from .views import CartRetrieveApiView, CartItemCreateAPIView, CartItemUpdatedAPIView, CartItemDeleteAPIView

app_name = 'carts'


urlpatterns = [
    path('', CartRetrieveApiView.as_view(), name='cart-detail'),
    path('items/create', CartItemCreateAPIView.as_view(), name='cart-item-add'),
    path('items/<int:pk>/update', CartItemUpdatedAPIView.as_view(), name='cart-item-update'),
    path('items/<int:pk>/delete', CartItemDeleteAPIView.as_view(), name='cart-item-delete'),
    
    
]