from django.db import models  # type: ignore
from django.contrib.auth.models import User #type:ignore
from decimal import Decimal #type:ignore
from django.conf import settings #type:ignore

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_veg = models.BooleanField(default=True)

    category = models.CharField(max_length=50, choices=[
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('meals', 'Meals'),
        ('desserts', 'Desserts'),
    ], default='meals')

    image_url = models.URLField(blank=True, null=True)  

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"



class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField()

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")
    full_name = models.CharField(max_length=255, default="Unknown")
    email = models.EmailField(default='default@example.com')
    address = models.CharField(max_length=255, default='Default Address')
    phone = models.CharField(max_length=15,default='null')  # New field for phone number
    payment_method = models.CharField(max_length=255, default="Not Specified")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(MenuItem, on_delete=models.CASCADE)  # Assuming `MenuItem` is the product model
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"