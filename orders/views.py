# from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.template.defaultfilters import register

from inventory.models import Variety
from orders.models import RestaurantAccount, Order, Product, HarvestedCropProduct, LiveCropProduct, MicrogreenSize, \
    TrayType, Setting
from orders.forms import *
from datetime import date, datetime, timedelta
# from dateutil import parser
# from google_sheets.upload_to_sheet import upload_data_to_sheets
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import re


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
    if request.method == "GET":
        stuff_to_display = []
        tags = []
        for variety in Variety.objects.all():
            tags = []
            products = HarvestedCropProduct.objects.filter(variety=variety)
            price = products.order_by('price')[0].price if products.exists() else 0
            if products.exists():
                # Get some tags
                for tag in products[0].tags.all():
                    print(products[0].name)
                    tags.append({"name": tag.name, "color": tag.color})
            print(tags)
            stuff_to_display.append((variety, price, tags))

        return render(request, "orders/shop.html", context={'products_to_display': stuff_to_display, 'i': 0})


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


@staff_member_required
def dashboard(request):
    return render(request, "orders/dashboard.html", context={})


@staff_member_required
def add_product(request):
    if request.method == 'GET':
        variety_list = []
        for v in Variety.objects.all().order_by('name'):
            variety_list.append(v.name)
        sizes = []
        for s in MicrogreenSize.objects.all().order_by('name'):
            sizes.append(s.name)
        tray_types = []
        for t in TrayType.objects.all().order_by('name'):
            tray_types.append(t.name)
        product_form = AddProductForm()
        return render(request, "orders/add_product.html", context={"product_form": product_form,
                                                                   "varieties": variety_list,
                                                                   "tray_types": tray_types,
                                                                   "sizes": sizes})
    if request.method == 'POST':
        variety_list = []
        for v in Variety.objects.all().order_by('name'):
            variety_list.append(v.name)
        sizes = []
        for s in MicrogreenSize.objects.all().order_by('name'):
            sizes.append(s.name)
        tray_types = []
        for t in TrayType.objects.all().order_by('name'):
            tray_types.append(t.name)
        product_form = AddProductForm()
        form = AddProductForm(request.POST)
        if form.is_valid():
            print(request.POST)
            fields = request.POST
            product_name = fields['product_name']
            alph_num_name = alphanumeric(product_name)
            price = fields['price']
            if fields['select-product-type'] == 'Live Crop Product':
                variety = Variety.objects.get(name=fields['variety'])
                size = MicrogreenSize.objects.get(name=fields['size'])
                tray_type = TrayType.objects.get(name=fields['tray-type'])
                LiveCropProduct.objects.create(name=product_name, alph_num_name=alph_num_name, price=price,
                                               variety=variety,
                                               size=size, tray_type=tray_type)
            elif fields['select-product-type'] == 'Harvested Crop Product':
                variety = Variety.objects.get(name=fields['variety'])
                size = MicrogreenSize.objects.get(name=fields['size'])
                weight = int(fields['weight'])
                HarvestedCropProduct.objects.create(name=product_name, alph_num_name=alph_num_name, price=price,
                                                    variety=variety,
                                                    size=size, weight=weight)
            elif fields['select-product-type'] == 'Other Product':
                Product.objects.create(name=product_name, price=price, alph_num_name=alph_num_name)

            message = "Successfully added " + product_name + " to your "
            return render(request, "orders/add_product.html", context={"product_form": product_form,
                                                                       "varieties": variety_list,
                                                                       "tray_types": tray_types,
                                                                       "sizes": sizes,
                                                                       "success": message})
        else:
            message = "Something went wrong."
            print(message)
            return render(request, "orders/add_product.html", context={"product_form": product_form,
                                                                       "varieties": variety_list,
                                                                       "tray_types": tray_types,
                                                                       "sizes": sizes,
                                                                       "error": message})


def alphanumeric(s):
    """Convert string to alphanumeric characters"""
    return re.sub(r'\W+', '', s)


@staff_member_required
def products(request):
    if request.method == 'GET':
        other_products = []
        for product in Product.objects.all():
            if not LiveCropProduct.objects.filter(id=product.id).exists() \
                    and not HarvestedCropProduct.objects.filter(id=product.id).exists():
                other_products.append(product)
        return render(request, "orders/products.html", context={"live_crop_products": LiveCropProduct.objects.all(),
                                                                "harvested_crop_products": HarvestedCropProduct.objects.all(),
                                                                "other_products": other_products})
    # if request.method == 'POST':
    #     live_crop_products = []
    #     harvested_crop_products = []
    #     other_products = []
    #     return render(request, "inventory/products.html", context={"live_crop_products": live_crop_products,
    #                                                               "harvested_crop_products": harvested_crop_products,
    #                                                               "other_products": other_products})


@staff_member_required
def orders_settings(request):
    DAYS_OF_WEEK = (
        (0, 'Sunday'),
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )

    if request.method == "GET":
        delivery_days = eval(Setting.objects.get(name='DELIVERY_DAYS').value)
        seeding_days = eval(Setting.objects.get(name='SEEDING_DAYS').value)
        lead_time = eval(Setting.objects.get(name='CONSTANT_LEAD_DAYS').value)
        return render(request, "orders/orders_settings.html",
                      context={"delivery_days": delivery_days, "seeding_days": seeding_days, "weekdays": DAYS_OF_WEEK,
                               "lead_time": lead_time})
    if request.method == "POST":
        delivery_days = [int(i) for i in request.POST.getlist('delivery')]
        seeding_days = [int(i) for i in request.POST.getlist('seeding')]
        constant_lead = request.POST.get('constant-lead')
        delivery_setting = Setting.objects.get(name='DELIVERY_DAYS')
        seeding_setting = Setting.objects.get(name='SEEDING_DAYS')
        constant_lead_setting = Setting.objects.get(name='CONSTANT_LEAD_DAYS')
        delivery_setting.value = delivery_days
        seeding_setting.value = seeding_days
        constant_lead_setting.value = constant_lead if int(constant_lead) >= 0 else "0"
        delivery_setting.save()
        seeding_setting.save()
        constant_lead_setting.save()
        return redirect(orders_settings)


@staff_member_required
def orders(request):
    if request.method == "GET":
        return render(request, "orders/orders.html", context={"orders": Order.objects.all().order_by('delivery_date')})


@staff_member_required
def customers(request):
    return render(request, "orders/customers.html", context={'customers': RestaurantAccount.objects.all()})


def product_details(request, product_name):
    if request.method == "GET":
        logged_in = request.user.is_authenticated
        try:
            # Get Variety object and
            # Find 'HarvestedCropProduct' or LiveCropProduct' for the given variety
            variety = Variety.objects.get(name=product_name)
            crop_products = []
            crop_products += variety.live_crop_products.all()
            crop_products += variety.harvested_crop_products.all()
            other_product = None
            tags = []
            # If products for the given variety can be found...
            if crop_products:
                lowest_price = crop_products[0].price
                for product in crop_products:
                    tags += product.tags.all()
                    lowest_price = product.price if product.price < lowest_price else lowest_price
                tags = set(tags)
            else:
                lowest_price = None
        except Variety.DoesNotExist:
            # 'Other' type of product
            variety = None
            crop_products = None
            other_product = Product.objects.get(name=product_name)
            lowest_price = product.price
            tags = product.tags.all()
            pass
        return render(request, "orders/product_details.html", context={"logged_in": logged_in,
                                                                       "order_form": OrderForm(),
                                                                       "variety": variety,
                                                                       "crop_products": crop_products,
                                                                       "other_product": other_product,
                                                                       "lowest_price": lowest_price,
                                                                       "tags": tags})
    if request.method == "POST":
        return redirect(cart)
