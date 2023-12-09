from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer,Product,Category,Cart,CartItem

admin.site.register(Customer,UserAdmin)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
# Register your models here.
