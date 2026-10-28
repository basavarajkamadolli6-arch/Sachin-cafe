from django.db import models
from django.contrib.auth.models import User
class Product(models.Model):
 CATEGORY_CHOICES=[('tea','Tea'),('coffee','Coffee'),('cold','Cold Drinks'),('snack','Snacks'),('dessert','Desserts')]
 name=models.CharField(max_length=120,unique=True)
 description=models.CharField(max_length=255,blank=True)
 category=models.CharField(max_length=20,choices=CATEGORY_CHOICES)
 price=models.DecimalField(max_digits=8,decimal_places=2)
 image_url=models.URLField(blank=True)
 available=models.BooleanField(default=True)
 featured=models.BooleanField(default=False)
 def __str__(self):return self.name
class Order(models.Model):
 STATUS=[('pending','Pending'),('preparing','Preparing'),('ready','Ready'),('completed','Completed'),('cancelled','Cancelled')]
 PAYMENT=[('cash','Pay at Cafe'),('razorpay','Razorpay')]
 PAYMENT_STATUS=[('unpaid','Unpaid'),('paid','Paid')]
 user=models.ForeignKey(User,on_delete=models.PROTECT,related_name='cafe_orders')
 name=models.CharField(max_length=120)
 phone=models.CharField(max_length=15)
 order_type=models.CharField(max_length=15,choices=[('dinein','Dine In'),('takeaway','Takeaway')])
 notes=models.TextField(blank=True)
 status=models.CharField(max_length=15,choices=STATUS,default='pending')
 payment_method=models.CharField(max_length=15,choices=PAYMENT,default='cash')
 payment_status=models.CharField(max_length=10,choices=PAYMENT_STATUS,default='unpaid')
 subtotal=models.DecimalField(max_digits=9,decimal_places=2)
 tax=models.DecimalField(max_digits=9,decimal_places=2)
 total=models.DecimalField(max_digits=9,decimal_places=2)
 razorpay_order_id=models.CharField(max_length=120,blank=True,unique=True,null=True)
 razorpay_payment_id=models.CharField(max_length=120,blank=True)
 created_at=models.DateTimeField(auto_now_add=True)
 def __str__(self):return f'Order #{self.pk}'
class OrderItem(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
 product=models.ForeignKey(Product,on_delete=models.PROTECT)
 name=models.CharField(max_length=120)
 price=models.DecimalField(max_digits=8,decimal_places=2)
 quantity=models.PositiveIntegerField()
