from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class Customer(AbstractUser):
    id = models.AutoField(primary_key=True) 
    username = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=100, null=True)
    date_of_birth = models.DateField(default='2000-01-01', null=True)
    email = models.EmailField(max_length=100, default="email@email.com")

    def __str__(self):
        return f"{self.username}"

class Product(models.Model):
    
    category = models.ForeignKey('Category',on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100, null=False)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to="product_images", default="product_images/product_placeholder.png")

    def __str__(self):
        return f'{self.name}'

class Category(models.Model):    
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=200)
    
    def __str__(self):
        return f'{self.name}'

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')
    

    def __str__(self):
        return f'Cart for {self.customer.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in cart for {self.cart.customer.username}'

    def total_price(self):
        return self.quantity * self.product.price

    def update_quantity(self, quantity):
        self.quantity = quantity
        self.save()

    def increment_quantity(self):
        self.quantity += 1
        self.save()

    def decrement_quantity(self):
        if self.quantity > 1:
            self.quantity -= 1
            self.save()

    @property
    def subtotal(self):
        return self.total_price()

    class Meta:
        unique_together = ('cart', 'product')
