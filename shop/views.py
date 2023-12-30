import json
from rest_framework import status , generics,viewsets
from django.shortcuts import render
from .models import Category, Product,Cart,CartItem
from .serializers import ProductSerializer, CategorySerializer , CustomerSerializer ,CartItemSerializer,CartSerializer
# from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout,get_user_model
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import Customer
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import action
Customer = get_user_model()
    
@api_view(['GET', 'POST'])
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
def products(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        maxprice = request.GET.get('maxprice')
        category = request.GET.get('category')
        all_products = Product.objects.all()
        # search all product that name contains search parameter
        if search:
            all_products = all_products.filter(name__contains=search)
        # search all product that price <= maxprice (price__lte=maxprice)
        if maxprice:
            all_products = all_products.filter(price__lte=maxprice)
        if category:
            all_products = all_products.filter(category__id=category)

        all_products_json = ProductSerializer(all_products, many=True).data
        return Response(all_products_json)
    elif request.method == 'POST':
        # this line creates a serializer object from json data
        serializer = ProductSerializer(data=request.data)
        # this line checkes validity of json data
        if serializer.is_valid():
            # the serializer.save - saves a new product object
            serializer.save()
            # returns the object that was created including id
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # if not valid. return errors.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
    # get object from db by id
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    # GET
    if request.method == 'GET':
        # create serializer from object
        serializer = ProductSerializer(product)
        # return json using serializer
        return Response(serializer.data)
    # PUT
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # DELETE
    elif request.method == 'DELETE':
        # product.is_active = False
        # product.save()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view()
def categories(request):
    search = request.GET.get('search')
    all_categories = Category.objects.all()
    if search:
        all_categories = all_categories.filter(name__contains=search)
    all_categories_json = CategorySerializer(all_categories, many=True).data
    return Response(all_categories_json)
User = get_user_model()
@api_view(['POST'])
@require_POST
def login_view(request):

   
    username = request.data.get('username')
    password = request.data.get('password')
    print(username,password)
    user = authenticate(username=username, password=password)
    print(user)
    if user:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({'access_token': access_token}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def logout_view(request):
    request.auth.delete()
    logout(request)
    return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        city = data.get('city')
        date_of_birth = data.get('date_of_birth')

        # Check if passwords match
        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user or email already exists
        if Customer.objects.filter(username=username).exists() or Customer.objects.filter(email=email).exists():
            return Response({'error': 'User or email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user and customer
        user = Customer.objects.create_user(username=username,city=city, password=password , date_of_birth=date_of_birth, email=email)
        return Response(status=status.HTTP_201_CREATED)
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    # Custom method to get the cart for the currently logged-in user
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticated])
    def get_user_cart(self, request):
        user = request.user
        cart = Cart.objects.get(customer=user)
        serializer = self.serializer_class(cart)
        return Response(serializer.data)

    # Override the create method to associate the new cart with the logged-in user
    def create(self, request, *args, **kwargs):
        user = request.user
        request.data['customer'] = user.id
        return super().create(request, *args, **kwargs)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    # Custom method to get cart items for a specific cart
    
    def get_cart_items(self, request, cart_id):
        cart_items = CartItem.objects.filter(cart__id=cart_id)
        serializer = self.serializer_class(cart_items, many=True)
        return Response(serializer.data)
    
    # Override the create method to associate the new cart item with the corresponding cart
    def create(self, request, *args, **kwargs):
        cart_id = request.data.get('cart')
        cart = Cart.objects.get(id=cart_id)
        request.data['cart'] = cart.id
        return super().create(request, *args, **kwargs)
    @action(detail=True, methods=['delete'])
    def delete_all_items(self, request, pk=None):
        cart_items = CartItem.objects.filter(cart__id=pk)
        cart_items.delete()
        return Response(status=204)