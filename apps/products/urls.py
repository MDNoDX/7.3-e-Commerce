from django.urls import path
from apps.products.views import (
    ProductListAPIView, 
    ProductCreateAPIView,
    ProductDetailAPIView,
    ProductUpdateAPIView,
    ProductPartialUpdateAPIView,
    ProductDeleteAPIView
)

app_name = 'products'

urlpatterns = [
    path('', ProductListAPIView.as_view(), name='list'),
    path('create/', ProductCreateAPIView.as_view(), name='create'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='detail'),
    path('<int:pk>/update/', ProductUpdateAPIView.as_view(), name='update'),
    path('<int:pk>/patch/', ProductPartialUpdateAPIView.as_view(), name='patch'),
    path('<int:pk>/delete/', ProductDeleteAPIView.as_view(), name='delete'),
]