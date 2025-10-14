from django.shortcuts import render
from django.utils import timezone
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from apps.carts.models import Cart
from apps.orders.models import OrderItem, Order
from apps.orders.serializers import  OrderCreateSerializer, OrderListSerializer, OrderDetailSerializer
from .pagination import OrderPagination
# Create your views here.
    
class OrderCreateAPIView(GenericAPIView, CreateModelMixin):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    
    
    def perform_create(self, serializer):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_items = cart.items.all()
        
        
        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")
        
        for item in cart_items:
            if item.quantity > item.product.stock_quantity:
                raise serializers.ValidationError(f"Not enough stock for {item.product.name}. Only {item.product.stock_quantity} left.")
            
            
        timestamp = int(timezone.now().timestamp())
        order_number = f"ORD - {user.id}-{timestamp}"
        
        total_amount = 0
        
        for item in cart_items:
            price = item.product.price
            if item.product.discount_percentage:
                price -= item.product.price * item.product.discount_percentage / 100
            total_amount += price * item.quantity
            
            
        order = serializer.save(
            user=user, order_number=order_number,
            total_amount=round(total_amount, 2),
            status='pending'
        )
        
        
        for item in cart_items:
            product = item.product
            price = product.price
            if product.discount_percentage:
                price -= product.price * product.discount_percentage / 100
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=price,
                subtotal=price * item.quantity
            )
            product.stock_quantity -= item.quantity
            product.save()
            
        
        cart.items.all().delete()
        
        return order
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OrderListAPIView(GenericAPIView, ListModelMixin):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        return self.request.user.orders.all().order_by('-created_at')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)  
    
    

class OrderDetailAPIView(GenericAPIView, RetrieveModelMixin):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    
    
    
    def get_queryset(self):
        return self.request.user.orders.all()
    
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    
class OrderCancelAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer
    
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        return self.request.user.orders.get(pk=pk)
    
    
    def post(self, request, *args, **kwargs):
        try:
            order = self.get_object()
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        
        if order.status not in ['pending', 'processing']:
            return Response(
                {"error": "Order cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()

       
        order.status = 'cancelled'
        order.save()

        serializer = self.get_serializer(order)
        return Response(
            {
                "message": "Order cancelled successfully",
                "order": serializer.data
            },
            status=status.HTTP_200_OK
        )   