from rest_framework import serializers
from django.utils.text import slugify
from decimal import Decimal
from apps.products.models import Product, Category, Brand, ProductImage
from apps.reviews.models import ProductReview

class CategoryNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BrandNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_primary', 'order']

class ProductReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview.user.field.related_model
        fields = ['id', 'username']

class ProductReviewSerializer(serializers.ModelSerializer):
    user = ProductReviewUserSerializer(read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']

class RelatedProductSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'final_price', 'primary_image']
    
    def get_final_price(self, obj):
        discount_decimal = Decimal(obj.discount_percentage) / Decimal(100)
        return obj.price * (Decimal(1) - discount_decimal)
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        return primary_image.image_url if primary_image else None

class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryNestedSerializer(read_only=True)
    brand = BrandNestedSerializer(read_only=True)
    final_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'brand',
            'price', 'discount_percentage', 'final_price', 'stock_quantity',
            'in_stock', 'is_featured', 'primary_image', 'reviews_count',
            'average_rating', 'created_at', 'updated_at'
        ]
    
    def get_final_price(self, obj):
        discount_decimal = Decimal(obj.discount_percentage) / Decimal(100)
        return obj.price * (Decimal(1) - discount_decimal)
    
    def get_in_stock(self, obj):
        return obj.stock_quantity > 0
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        return primary_image.image_url if primary_image else None
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

class ProductDetailResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField()
    category = CategoryNestedSerializer()
    brand = BrandNestedSerializer()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = serializers.IntegerField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = serializers.IntegerField()
    in_stock = serializers.BooleanField()
    is_featured = serializers.BooleanField()
    images = ProductImageSerializer(many=True)
    reviews = ProductReviewSerializer(many=True)
    reviews_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    related_products = RelatedProductSerializer(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

class ProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'slug': {'read_only': True},
        }

    def create(self, validated_data):
        slug = slugify(validated_data.get('name'))
        
        while Product.objects.filter(slug=slug).exists():
            random = Product.generate_id()
            slug = f"{slug}-{random}"

        validated_data['slug'] = slug
        return Product.objects.create(**validated_data)

class ProductCreateResponseSerializer(serializers.ModelSerializer):
    category = CategoryNestedSerializer(read_only=True)
    brand = BrandNestedSerializer(read_only=True)
    final_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'brand',
            'price', 'discount_percentage', 'final_price', 'stock_quantity',
            'in_stock', 'is_featured', 'created_at', 'updated_at'
        ]
    
    def get_final_price(self, obj):
        discount_decimal = Decimal(obj.discount_percentage) / Decimal(100)
        return obj.price * (Decimal(1) - discount_decimal)
    
    def get_in_stock(self, obj):
        return obj.stock_quantity > 0

class ProductFilterSerializer(serializers.Serializer):
    category = serializers.IntegerField(required=False)
    brand = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    is_featured = serializers.BooleanField(required=False)
    search = serializers.CharField(required=False)
    
    def filter_products(self):
        products = Product.objects.filter(is_active=True)
        
        category = self.validated_data.get('category')
        if category:
            products = products.filter(category_id=category)
        
        brand = self.validated_data.get('brand')
        if brand:
            products = products.filter(brand_id=brand)
        
        min_price = self.validated_data.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        
        max_price = self.validated_data.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
        
        is_featured = self.validated_data.get('is_featured')
        if is_featured:
            products = products.filter(is_featured=True)
        
        search = self.validated_data.get('search')
        if search:
            products = products.filter(name__icontains=search) | products.filter(description__icontains=search)
        
        return products