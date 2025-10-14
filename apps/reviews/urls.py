from django.urls import path
from apps.reviews.views import (
    ProductReviewCreateView,
    ProductReviewListView,
    ProductReviewUpdateView,
    ProductReviewDeleteView
)

app_name = 'reviews'

urlpatterns = [
    path('products/<int:product_id>/reviews/', ProductReviewListView.as_view(), name='list'),
    path('products/<int:product_id>/reviews/create/', ProductReviewCreateView.as_view(), name='create'),
    path('reviews/<int:pk>/', ProductReviewUpdateView.as_view(), name='update'),
    path('reviews/<int:pk>/delete/', ProductReviewDeleteView.as_view(), name='delete'),
]