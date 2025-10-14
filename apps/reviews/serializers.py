from rest_framework import serializers
from apps.reviews.models import ProductReview
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['user', 'is_verified_purchase', 'created_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters")
        return value
    
    def validate_comment(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters")
        return value

class ProductReviewListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    helpful_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'user', 'rating', 'title', 'comment', 
            'is_verified_purchase', 'created_at', 'helpful_count'
        ]
    
    def get_helpful_count(self, obj):
        return 0