from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from apps.products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source = 'product.name', read_only = True)




class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'shipping_address', 'phone', 'notes', 'status', 'total_amount', 'created_at', 'items'
        ]
        
        
    def validate_phone(self, value):
        if not value.startswith('+998'):
            raise serializers.ValidationError('Phone number must start with +998')
        
        
        if len(value) != 13:
            raise serializers.ValidationError('Phone number must be exactly 13 characters long!')
        
        if not value[4:].isdigit():
            raise serializers.ValidationError('Phone number must contain only digits after +998.')
        
        
    def validate_shipping_address(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Shipping address must contain at least 10 characters.")
        
        return value
    


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'total_amount', 'status',
            'status_display', 'items_count', 'created_at', 'can_cancel'
        ]
        
        def get_items_count(self, obj):
            return obj.items.count()
        
        
        def get_can_cancel(self, obj):
            return obj.status in ['pending', 'processing']
        
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'primary_image']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'discount_percentage', 'subtotal']

    def get_subtotal(self, obj):
        discount = obj.discount_percentage or 0
        discounted_price = obj.price * (1 - discount / 100)
        return discounted_price * obj.quantity
    
    

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        
        

class OrderDetailSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    items = OrderItemSerializer(many=True, read_only=True)     
    
    
    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'user',
            'items',
            'total_amount',
            'status',
            'shipping_address',
            'phone',
            'notes',
            'created_at',
            'updated_at'
        ]
        
        