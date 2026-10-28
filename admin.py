from django.contrib import admin
from .models import Product,Order,OrderItem
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
 list_display=('name','category','price','available','featured')
 list_filter=('category','available','featured')
 search_fields=('name','description')
class OrderItemInline(admin.TabularInline):
 model=OrderItem
 extra=0
 readonly_fields=('product','name','price','quantity')
 can_delete=False
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
 list_display=('id','user','total','status','payment_method','payment_status','created_at')
 list_filter=('status','payment_method','payment_status')
 readonly_fields=('user','name','phone','order_type','notes','subtotal','tax','total','payment_method','payment_status','razorpay_order_id','razorpay_payment_id','created_at')
 inlines=[OrderItemInline]
