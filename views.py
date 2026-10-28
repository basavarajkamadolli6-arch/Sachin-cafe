import json,os,re
from decimal import Decimal,ROUND_HALF_UP
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse,HttpResponseBadRequest
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product,Order,OrderItem

def home(request):
 return render(request,'cafe/index.html',{'featured':Product.objects.filter(available=True,featured=True)[:4]})
def menu(request):
 products=Product.objects.filter(available=True).order_by('category','price')
 return render(request,'cafe/menu.html',{'products':products,'address':settings.CAFE_ADDRESS})
def register(request):
 if request.user.is_authenticated:return redirect('menu')
 form=UserCreationForm(request.POST or None)
 if request.method=='POST' and form.is_valid():
  user=form.save();login(request,user);messages.success(request,'Welcome to Sachin Cafe!');return redirect('menu')
 return render(request,'registration/register.html',{'form':form})
def cart_data(request):
 raw=request.session.get('cart',{})
 products=Product.objects.filter(pk__in=raw.keys(),available=True)
 items=[];subtotal=Decimal('0.00')
 for p in products:
  qty=max(1,min(20,int(raw.get(str(p.pk),0))))
  line=p.price*qty;subtotal+=line
  items.append({'product':p,'qty':qty,'line':line})
 tax=(subtotal*Decimal('0.05')).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
 return {'items':items,'subtotal':subtotal,'tax':tax,'total':subtotal+tax}

def cart_view(request):return render(request,'cafe/cart.html',cart_data(request))
@require_POST
def cart_update(request):
 try:
  pid=int(request.POST.get('product_id','0'));qty=int(request.POST.get('quantity','0'))
 except ValueError:return HttpResponseBadRequest('Invalid quantity')
 if qty<0 or qty>20:return HttpResponseBadRequest('Quantity must be 0–20')
 product=get_object_or_404(Product,pk=pid,available=True)
 cart=request.session.get('cart',{})
 if request.POST.get('next')=='/menu/' and qty==1:
  qty=min(20,int(cart.get(str(product.pk),0))+1)
 if qty:cart[str(product.pk)]=qty
 else:cart.pop(str(product.pk),None)
 request.session['cart']=cart
 return redirect(request.POST.get('next') if request.POST.get('next') in ['/menu/','/cart/'] else 'cart')
@login_required
def checkout(request):
 data=cart_data(request)
 if not data['items']:
  messages.error(request,'Add something to your cart first.');return redirect('menu')
 if request.method=='POST':
  name=request.POST.get('name','').strip()[:120];phone=request.POST.get('phone','').strip()
  kind=request.POST.get('order_type','takeaway');method=request.POST.get('payment_method','cash')
  if not name or not re.fullmatch(r'[0-9+\- ]{10,15}',phone) or kind not in ('dinein','takeaway') or method not in ('cash','razorpay'):
   messages.error(request,'Please enter valid checkout details.');return render(request,'cafe/checkout.html',{**data,'razorpay_enabled':bool(os.getenv('RAZORPAY_KEY_ID') and os.getenv('RAZORPAY_KEY_SECRET'))})
  if method=='razorpay' and not (os.getenv('RAZORPAY_KEY_ID') and os.getenv('RAZORPAY_KEY_SECRET')):
   messages.error(request,'Online payment is not configured. Choose Pay at Cafe.');return redirect('checkout')
  with transaction.atomic():
   order=Order.objects.create(user=request.user,name=name,phone=phone,order_type=kind,notes=request.POST.get('notes','')[:1000],payment_method=method,subtotal=data['subtotal'],tax=data['tax'],total=data['total'])
   for item in data['items']:
    p=item['product'];OrderItem.objects.create(order=order,product=p,name=p.name,price=p.price,quantity=item['qty'])
  request.session['cart']={}
  if method=='razorpay':
   messages.info(request,'Order created. Click Pay Online in My Orders to complete payment.')
   return redirect('orders')
  messages.success(request,f'Order #{order.pk} created. Pay at cafe on pickup/dine-in.')
  return redirect('orders')
 return render(request,'cafe/checkout.html',{**data,'razorpay_enabled':bool(os.getenv('RAZORPAY_KEY_ID') and os.getenv('RAZORPAY_KEY_SECRET'))})
@login_required
def orders(request):
 return render(request,'cafe/orders.html',{'orders':Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at'),'razorpay_key':os.getenv('RAZORPAY_KEY_ID','')})
@user_passes_test(lambda u:u.is_active and u.is_staff,login_url='login')
def dashboard(request):
 qs=Order.objects.order_by('-created_at')
 return render(request,'cafe/dashboard.html',{'orders':qs[:60],'orders_count':qs.count(),'revenue':Order.objects.filter(payment_status='paid').aggregate(value=Sum('total'))['value'] or 0,'products_count':Product.objects.count()})
@require_POST
@user_passes_test(lambda u:u.is_active and u.is_staff,login_url='login')
def change_status(request,pk):
 order=get_object_or_404(Order,pk=pk)
 if request.POST.get('status') in dict(Order.STATUS):
  order.status=request.POST['status'];order.save(update_fields=['status'])
 return redirect('dashboard')

def fallback_reply(text):
 lower=text.lower()
 products=list(Product.objects.filter(available=True))
 if any(k in lower for k in ['hi','hello','hey','namaste','ನಮಸ್ಕಾರ']):return 'Hello! ☕ Welcome to Sachin Cafe. Tell me your budget or ask about tea, coffee or snacks.'
 budget=re.search(r'(?:₹|rs\.?\s*|under\s*|below\s*|budget\s*)(\d{1,4})',lower)
 if budget:
  amount=int(budget.group(1));found=sorted((p for p in products if p.price<=amount),key=lambda p:p.price)
  return ('Under ₹'+str(amount)+': '+', '.join(f'{p.name} ₹{p.price:g}' for p in found[:8])) if found else 'No products in that budget. Try ₹20 or more.'
 terms={'tea':['tea','chai','ಚಹಾ'],'coffee':['coffee','ಕಾಫಿ'],'snack':['snack','food','hungry','ತಿಂಡಿ'],'dessert':['cake','dessert','sweet']}
 for category,words in terms.items():
  if any(w in lower for w in words):
   cat='snack' if category=='snack' else category
   found=[p for p in products if p.category==cat]
   return 'Try '+', '.join(f'{p.name} ₹{p.price:g}' for p in found[:7])+'. Add your favorites from the menu!'
 return 'I can recommend tea, coffee and snacks by budget. Try “tea under ₹30”, “coffee”, or “snacks”. Configure OPENAI_API_KEY for full AI conversations.'
@require_POST
def chat(request):
 try:body=json.loads(request.body);question=str(body.get('message','')).strip()
 except (ValueError,TypeError):return JsonResponse({'error':'Invalid request'},status=400)
 if not question or len(question)>500:return JsonResponse({'error':'Message must be 1–500 characters'},status=400)
 key=os.getenv('OPENAI_API_KEY','')
 if key:
  menu_text='\n'.join(f'{p.name} ({p.category}) ₹{p.price} — {p.description}' for p in Product.objects.filter(available=True))
  payload={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'messages':[{'role':'system','content':'You are Sachin Cafe assistant. Be friendly, concise, reply in the user language (Kannada or English). Only recommend items and prices in this current menu. Do not invent discounts, live availability, payments, delivery, or address. Never ask for card details. Menu:\n'+menu_text},{'role':'user','content':question}],'max_tokens':250}
  try:
   req=Request('https://api.openai.com/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
   with urlopen(req,timeout=12) as response:result=json.load(response)
   return JsonResponse({'reply':result['choices'][0]['message']['content'],'mode':'ai'})
  except (URLError,HTTPError,KeyError,ValueError,TimeoutError):pass
 return JsonResponse({'reply':fallback_reply(question),'mode':'basic'})

@login_required
@require_POST
def payment_create(request):
 if not (os.getenv('RAZORPAY_KEY_ID') and os.getenv('RAZORPAY_KEY_SECRET')):return JsonResponse({'error':'Razorpay not configured'},status=400)
 try:
  import razorpay
  order=get_object_or_404(Order,pk=int(request.POST.get('order_id',0)),user=request.user,payment_method='razorpay',payment_status='unpaid')
  client=razorpay.Client(auth=(os.getenv('RAZORPAY_KEY_ID'),os.getenv('RAZORPAY_KEY_SECRET')))
  if order.razorpay_order_id:
   razorpay_id=order.razorpay_order_id
  else:
   rp=client.order.create({'amount':int(order.total*100),'currency':'INR','receipt':f'cafe_{order.pk}'})
   razorpay_id=rp['id'];order.razorpay_order_id=razorpay_id;order.save(update_fields=['razorpay_order_id'])
  return JsonResponse({'key':os.getenv('RAZORPAY_KEY_ID'),'amount':int(order.total*100),'currency':'INR','order_id':razorpay_id,'cafe_order_id':order.pk,'name':order.name})
 except (ValueError,ImportError):return JsonResponse({'error':'Invalid order or payment setup'},status=400)
 except Exception:return JsonResponse({'error':'Payment service temporarily unavailable'},status=502)
@login_required
@require_POST
def payment_verify(request):
 try:
  import razorpay
  data=json.loads(request.body)
  order=get_object_or_404(Order,pk=int(data['cafe_order_id']),user=request.user,payment_method='razorpay')
  if order.payment_status=='paid':return JsonResponse({'ok':True})
  if not order.razorpay_order_id or data['razorpay_order_id']!=order.razorpay_order_id:return JsonResponse({'error':'Order mismatch'},status=400)
  client=razorpay.Client(auth=(os.getenv('RAZORPAY_KEY_ID'),os.getenv('RAZORPAY_KEY_SECRET')))
  client.utility.verify_payment_signature({'razorpay_order_id':order.razorpay_order_id,'razorpay_payment_id':data['razorpay_payment_id'],'razorpay_signature':data['razorpay_signature']})
  payment=client.payment.fetch(data['razorpay_payment_id'])
  if payment.get('order_id')!=order.razorpay_order_id or payment.get('currency')!='INR' or int(payment.get('amount',0))!=int(order.total*100) or payment.get('status') not in ('authorized','captured'):
   return JsonResponse({'error':'Payment details could not be verified'},status=400)
  with transaction.atomic():
   order=Order.objects.select_for_update().get(pk=order.pk)
   order.payment_status='paid';order.razorpay_payment_id=data['razorpay_payment_id'];order.save(update_fields=['payment_status','razorpay_payment_id'])
  return JsonResponse({'ok':True})
 except Exception:return JsonResponse({'error':'Payment verification failed'},status=400)
