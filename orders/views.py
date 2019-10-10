# from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.template import RequestContext
from orders.models import RestaurantAccount, Order, Product, HarvestedCropProduct, LiveCropProduct
from orders.forms import OrderForm
from datetime import date, datetime, timedelta
# from dateutil import parser
# from google_sheets.upload_to_sheet import upload_data_to_sheets
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404
# import os
# import json

def orders_home(request):
    return render(request, "orders/index.html", context={})

def create_account(request):
    if request.method == "GET":
        return render(request, "orders/create_account.html")
    if request.method == "POST":
        try:
            user_name = request.POST.get('username')
            user_pass = request.POST.get('password')
            user_mail = request.POST.get('email')
            restaurant_name = request.POST.get('rest-name')
            restaurant_phone = request.POST.get('phone')
            user = User.objects.create_user(username=user_name,
                                            email=user_mail,
                                            password=user_pass)
            RestaurantAccount.objects.create(phone=restaurant_phone, restaurant_name=restaurant_name, user=user)
        except KeyError:
            pass
        except IntegrityError:
            error = "Account with this username already exists!"
            return render(request, "orders/create_account.html", context={"error": error})
        success_message = "Account created! Please log in."
        return render(request, "registration/login.html", context={"account_creation_success": success_message})


def shop(request):
    return render(request, "orders/shop.html", context={})

@login_required
def schedule(request):
    return render(request, "orders/schedule.html", context={})

@login_required
def account(request):
    return render(request, "orders/account.html", context={})

@login_required
def cart(request):
    if request.method == "GET":
        cart_orders = []
        for order in Order.objects.all():
            if order.account == request.user and not order.confirmed:
                print(order)
                cart_orders.append(order)
    return render(request, "orders/cart.html", context={"cart_orders": cart_orders})

@login_required
def create_order(request):
    if request.method == "GET":
        form = OrderForm()
        return render(request, "orders/create_order.html", context={"form": form})
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            delivery_date = form.cleaned_data["delivery_date"]
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]
            account = request.user
            if HarvestedCropProduct.objects.filter(id=product.id).exists():
                product = HarvestedCropProduct.objects.get(id=product.id)
            elif LiveCropProduct.objects.filter(id=product.id).exists():
                product = LiveCropProduct.objects.get(id=product.id)
            else:
                Order.objects.create(product=product, delivery_date=delivery_date, quantity=quantity, account=account)
                return render(request, "orders/cart.html", context={"form": form})
            soonest_delivery_date = datetime.now() + timedelta(product.variety.lead_time)
            if delivery_date < soonest_delivery_date.date():
                raise ValidationError('Delivery date does not comply with lead times.')
            Order.objects.create(product=product, delivery_date=delivery_date, quantity=quantity, account=account)
            return redirect(cart)
