from rest_framework import serializers
from .models import Wishlist
from apps.products.models import Product


class WishlistProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    added_to_wishlist_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'discount_percentage',
            'final_price', 'primary_image', 'in_stock',
            'average_rating', 'added_to_wishlist_at'
        ]

    def get_final_price(self, obj):
        if obj.discount_percentage:
            return obj.price - (obj.price * obj.discount_percentage / 100)
        return obj.price

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0


class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    products = WishlistProductSerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'products', 'products_count', 'created_at']

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username
        }

    def get_products_count(self, obj):
        return obj.products.count()
