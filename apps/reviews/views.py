from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from apps.reviews.models import ProductReview
from apps.products.models import Product
from apps.reviews.serializers import ProductReviewSerializer, ProductReviewListSerializer

class ProductReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductReviewSerializer

    def post(self, request, product_id):
        serializer = self.serializer_class(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found"}, status=404)
        
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return Response(
                {"detail": "You have already reviewed this product"}, 
                status=400
            )
        
        is_verified_purchase = False
        
        review = serializer.save(
            user=request.user,
            product=product,
            is_verified_purchase=is_verified_purchase
        )
        
        return Response(serializer.data, status=201)

class ProductReviewListView(APIView):
    serializer_class = ProductReviewListSerializer

    def get(self, request, product_id):
        reviews = ProductReview.objects.filter(product_id=product_id).order_by('-created_at')
        
        rating = request.GET.get('rating')
        if rating:
            reviews = reviews.filter(rating=rating)
        
        ordering = request.GET.get('ordering')
        if ordering in ['-created_at', 'created_at', '-rating', 'rating']:
            reviews = reviews.order_by(ordering)
        
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(reviews, request)
        
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = self.serializer_class(reviews, many=True)
        return Response({
            "count": reviews.count(),
            "results": serializer.data
        }, status=200)

class ProductReviewUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductReviewSerializer

    def put(self, request, pk):
        try:
            review = ProductReview.objects.get(pk=pk, user=request.user)
        except ProductReview.DoesNotExist:
            return Response({"detail": "Review not found"}, status=404)
        
        serializer = self.serializer_class(review, data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        return Response(serializer.data, status=200)

class ProductReviewDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            review = ProductReview.objects.get(pk=pk, user=request.user)
        except ProductReview.DoesNotExist:
            return Response({"detail": "Review not found"}, status=404)
        
        review.delete()
        return Response(status=204)