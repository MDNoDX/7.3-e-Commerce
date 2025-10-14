from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product


class ProductInCartSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'discount_percentage', 'final_price', 'primary_image', 'in_stock']
        
        
    def get_final_price(self, obj):
        if obj.discount_percentage:
            discounted = obj.price - (obj.price * obj.discount_percentage / 100)
            return round(discounted, 2)
        return obj.price
    
    
    def get_in_stock(self, obj):
        return obj.stock_quantity > 0
    
    
    def get_primary_image(self, obj):
         
        primary_img = obj.images.filter(is_primary=True).first()
        if primary_img:
            return primary_img.image_url
         
        first_img = obj.images.first()
        return first_img.image_url if first_img else None
    

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductInCartSerializer()
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal', 'added_at']
        
        
        def get_subtotal(self, obj):
            final_price = obj.product.price
            if obj.product.discount_percentage:
                final_price -= obj.product.price * obj.product.discount_percentage / 100
            return round(final_price * obj.quantity, 2)
        

class CartSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    items = CartItemSerializer(many=True)
    items_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items',
            'items_count', 'total_amount',
            'created_at', 'updated_at'
        ]
        
    def get_user(self, obj):
        user = obj.user
        return obj.user.username if obj.user else None
        
        
    def get_items_count(self, obj):
        return sum(item.quantity for item in obj.items.all())
        
        
    def get_total_amount(self, obj):
        total = 0
        for item in obj.items.all():
            price = item.product.price
            if item.product.discount_percentage:
                price -= item.product.price * item.product.discount_percentage / 100
            total += price * item.quantity
        return round(total, 2)
        
 
class CartItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
     
     
    class Meta:
         model = CartItem
         fields = ['product', 'quantity']
    
    
    def validate_product(self, value):
        if not value.is_active:
            raise serializers.ValidationError('This product is not active.')
        if value.stock_quantity <= 0:
            raise serializers.ValidationError('This product is out of stock.')
        return value
    
    
    def validate(self, attrs):
        product = attrs.get('product')  
        quantity = attrs.get('quantity')
        
        
        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                f"Only {product.stock_quantity} items left in stock."
            ) 
        return attrs
    


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
        
        
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError('Quantity canot be negative.')
        return value
    
    
    def validate(self, attrs):
        quantity = attrs.get('quantity')
        product = self.instance.product
        
        if quantity > product.stock_quality:
            raise serializers.ValidationError(
                f"Only {product.stock_quantity} items left in stock."
                
            )
        return attrs
    
