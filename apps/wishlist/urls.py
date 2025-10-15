from django.urls import path

from apps.wishlist.views import WishlistAddProductView, WishlistClearView, WishlistMoveToCartView, WishlistRemoveProductView, WishlistRetrieveView

app_name = 'wishlist'

urlpatterns = [
    path('', WishlistRetrieveView.as_view(), name='wishlist'),
    path('add/<int:product_id>/', WishlistAddProductView.as_view(), name='wishlist-add'),
    path('remove/<int:product_id>/', WishlistRemoveProductView.as_view(), name='wishlist-remove'),
    path('move-to-cart/<int:product_id>/', WishlistMoveToCartView.as_view(), name='wishlist-move-to-cart'), 
    path('clear/', WishlistClearView.as_view(), name='wishlist-clear'),
]