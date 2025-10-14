from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.products.models import Product, Category, Brand, ProductImage
from apps.reviews.models import ProductReview
from apps.products.serializers import (
    ProductListSerializer, 
    ProductModelSerializer, 
    ProductFilterSerializer,
    ProductCreateResponseSerializer,
    ProductDetailResponseSerializer,
    RelatedProductSerializer
)

class ProductListAPIView(APIView):
    def get(self, request):
        filter_serializer = ProductFilterSerializer(data=request.GET)
        
        if not filter_serializer.is_valid():
            return Response(filter_serializer.errors, status=400)
        
        products = filter_serializer.filter_products()
        
        if not products.exists():
            return Response({"detail": "Products not found"}, status=404)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=200)

class ProductCreateAPIView(APIView):
    serializer_class = ProductModelSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        errors = {}

        if not request.data.get('name'):
            errors['name'] = 'Name is required'

        price = request.data.get('price')
        if price:
            try:
                if float(price) <= 0:
                    errors['price'] = "Price must be greater than 0"
            except:
                errors['price'] = 'Invalid price format'

        stock_quantity = request.data.get('stock_quantity')
        if stock_quantity:
            try:
                if int(stock_quantity) < 0:
                    errors['stock_quantity'] = 'Stock quantity cannot be negative'
            except:
                errors['stock_quantity'] = 'Invalid stock quantity format'

        discount_percentage = request.data.get('discount_percentage', 0)
        if discount_percentage:
            try:
                if int(discount_percentage) < 0 or int(discount_percentage) > 100:
                    errors['discount_percentage'] = "Discount percentage must be between 0 and 100"
            except:
                errors['discount_percentage'] = "Invalid discount percentage format"

        category_id = request.data.get('category')
        if category_id and not Category.objects.filter(id=category_id).exists():
            errors['category'] = "Category does not exist"
        
        brand_id = request.data.get('brand')
        if brand_id and not Brand.objects.filter(id=brand_id).exists():
            errors['brand'] = "Brand does not exist"
        
        if errors:
            return Response({"error": errors}, status=400)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        product = serializer.save()

        response_serializer = ProductCreateResponseSerializer(product)
        return Response(response_serializer.data, status=201)

class ProductDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)

        from decimal import Decimal
        
        final_price = product.price * (100 - product.discount_percentage) / 100
        
        category_data = {
            'id': product.category.id,
            'name': product.category.name,
            'slug': product.category.slug,
            'parent': product.category.parent.name if product.category.parent else None
        }
        
        brand_data = {
            'id': product.brand.id,
            'name': product.brand.name,
            'logo': product.brand.logo,
            'website': product.brand.website
        }
        
        images_data = []
        for image in product.images.all():
            images_data.append({
                'id': image.id,
                'image_url': image.image_url,
                'is_primary': image.is_primary,
                'order': image.order
            })
        
        reviews_data = []
        for review in product.reviews.all().order_by('-created_at'):
            reviews_data.append({
                'id': review.id,
                'user': {
                    'id': review.user.id,
                    'username': review.user.username
                },
                'rating': review.rating,
                'title': review.title,
                'comment': review.comment,
                'is_verified_purchase': review.is_verified_purchase,
                'created_at': review.created_at
            })
        
        reviews_count = product.reviews.count()
        average_rating = sum(review.rating for review in product.reviews.all()) / reviews_count if reviews_count > 0 else 0
        
        related_products_data = []
        related_products = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(id=product.id)[:4]
        
        for related in related_products:
            primary_image = related.images.filter(is_primary=True).first()
            related_final_price = related.price * (100 - related.discount_percentage) / 100
            related_products_data.append({
                'id': related.id,
                'name': related.name,
                'price': str(related.price),
                'final_price': str(related_final_price),
                'primary_image': primary_image.image_url if primary_image else None
            })
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'category': category_data,
            'brand': brand_data,
            'price': str(product.price),
            'discount_percentage': product.discount_percentage,
            'final_price': str(final_price),
            'stock_quantity': product.stock_quantity,
            'in_stock': product.stock_quantity > 0,
            'is_featured': product.is_featured,
            'images': images_data,
            'reviews': reviews_data,
            'reviews_count': reviews_count,
            'average_rating': round(average_rating, 1),
            'related_products': related_products_data,
            'created_at': product.created_at,
            'updated_at': product.updated_at
        }
        
        return Response(product_data, status=200)

class ProductUpdateAPIView(APIView):
    serializer_class = ProductModelSerializer

    def put(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)
        
        serializer = self.serializer_class(product, data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        if 'name' in request.data and request.data['name'] != product.name:
            from django.utils.text import slugify
            new_slug = slugify(request.data['name'])
            if Product.objects.filter(slug=new_slug).exclude(pk=pk).exists():
                random = Product.generate_id()
                new_slug = f"{new_slug}-{random}"
            product.slug = new_slug
            product.save()
        
        serializer.save()

        response_serializer = ProductCreateResponseSerializer(serializer.instance)
        return Response(response_serializer.data, status=200)

class ProductPartialUpdateAPIView(APIView):
    serializer_class = ProductModelSerializer

    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)
        
        serializer = self.serializer_class(product, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        if 'name' in request.data and request.data['name'] != product.name:
            from django.utils.text import slugify
            new_slug = slugify(request.data['name'])
            if Product.objects.filter(slug=new_slug).exclude(pk=pk).exists():
                random = Product.generate_id()
                new_slug = f"{new_slug}-{random}"
            product.slug = new_slug
            product.save()
        
        serializer.save()

        response_serializer = ProductCreateResponseSerializer(serializer.instance)
        return Response(response_serializer.data, status=200)

class ProductDeleteAPIView(APIView):
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)
        
        product.is_active = False
        product.save()
        
        return Response({"message": "Product deleted successfully"}, status=204)