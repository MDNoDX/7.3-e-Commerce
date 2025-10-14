from django.shortcuts import render
from django.utils import timezone
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
# from apps.orders.models import Order, OrderItem
# from apps.orders.serializers import OrderCreateSerializer
from .serializers import CartSerializer, CartItemCreateSerializer, CartItemUpdateSerializer
from apps.products.models import Product


class CartRetrieveApiView(GenericAPIView, RetrieveModelMixin):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user = self.request.user)
        return cart
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    
class CartItemCreateAPIView(GenericAPIView, CreateModelMixin):
    serializer_class = CartItemCreateSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        return self.request.user.cart.items.all()

    
    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        
        
        existing_item = cart.items.filter(product=product).first()
        
        
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            
            
            if new_quantity > product.stock_quantity:
                raise serializers.ValidationError(f"Not enough stock. Only {product.stock_quantity} available.")
            
            
            existing_item.quantity = new_quantity
            existing_item.save()
            
        else:
            if quantity > product.stock_quantity:
                raise serializers.ValidationError(f"Not enough stock. Only {product.stock_quantity} available.")
            
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            
    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        
        cart = request.user.cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
        


class CartItemUpdatedAPIView(GenericAPIView, UpdateModelMixin):
    serializer_class = CartItemUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        return self.request.user.cart.items.all()
    
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
        if instance.quantity == 0:
            instance.delete()
            
    
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CartItemDeleteAPIView(GenericAPIView, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    
    
    
    def get_queryset(self):
        return self.request.user.cart.items.all()
    
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    
