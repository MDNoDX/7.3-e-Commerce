from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from apps.products.models import Product
from .models import Wishlist
from .serializers import WishlistSerializer
from apps.carts.models import Cart, CartItem


class WishlistRetrieveView(RetrieveAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist
    
    
class WishlistAddProductView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    
    
    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if wishlist.products.filter(pk=product_id).exists():
            return Response({"message": "Product already in wishlist."}, status=status.HTTP_200_OK)
        
        wishlist.products.add(product)
        return Response({"message": "Product added to wishlist."}, status=status.HTTP_201_CREATED)
    
    
class WishlistRemoveProductView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    
    
    def delete(self, request, product_id, *args, **kwargs):
        try:
            wishlist = request.user.wishlist
        except Wishlist.DoesNotExist:
            return Response({"error": "Wishlist not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        wishlist.products.remove(product)
        return Response({"message": "Product removed from wishlist."}, status=status.HTTP_200_OK)
    

class WishlistMoveToCartView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer
    
    
    
    
    def post(self, request, product_id, *args, **kwargs):
        
        try:
            product = Product.objects.get(pk=product_id)
            
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
        
        wishlist = request.user.wishlist
        
        
        if product not in wishlist.products.all():
            return Response({"error": "Product not in wishlist."}, status=status.HTTP_400_BAD_REQUEST)
        
        if product.stock_quanitity <= 0:
            return Response({"error": "Product is out of stock."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        wishlist.products.remove(product)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            
        return Response({
            'message': 'Product moved to cart successfully.',
            'cart_items_count': cart.items.count()
        }, status=status.HTTP_200_OK)


class WishlistClearView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            wishlist = request.user.wishlist
        except Wishlist.DoesNotExist:
            return Response({"error": "Wishlist not found."}, status=status.HTTP_404_NOT_FOUND)

        wishlist.products.clear()
        return Response({"message": "Wishlist cleared."}, status=status.HTTP_200_OK)
    
    