from django.shortcuts import render, redirect, get_object_or_404 # to redirect the user
from .models import ProductosEnBodega, Cart, CartItem, Cliente, Bodega, Orders, BodegaOrders, OrderItem
from django.urls import reverse

from .forms import RegistrationForm, ClientForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages # to send unique messages to the users

from itertools import chain
from random import shuffle

from django.conf import settings

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse

from django.core.mail import EmailMultiAlternatives #EmailMessage
from django.template.loader import render_to_string

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from ipregistry import IpregistryClient, NoCache

import base64
import requests

import re # regex

import json
from django.http import JsonResponse

# Global variable Loads STATIC_URL
STATIC_URL = settings.STATIC_URL

def save_store_location(request):
    if request.method== "POST" and request.is_ajax():
        # Stores variables in session
        bodega_name = request.POST['bodega_name']
        request.session['bodega_name'] = bodega_name
        id_bodega = request.POST['id_bodega']
        request.session['id_bodega'] = id_bodega
        if request.user.is_authenticated:
            print("Cliente identificado")
            cliente = Cliente.objects.all().filter(cl_user=request.user).first()
            cliente.cl_bodega_ID = id_bodega
            cliente.save()
        else:
            print("Usuario no identificado")
    else:
        message = "Not Ajax"
    return HttpResponse("")

def locate_user():
    client = IpregistryClient("2cc3d6z6ct2weq", cache=NoCache())
    ipInfo = client.lookup()
    user_longitude = ipInfo.location['longitude']
    user_latitude = ipInfo.location['latitude']
    return user_longitude, user_latitude

def homepage(request):
    # FUTURE IMPROVEMENT. IF ipregistry SERVER FAILS, OUR SITE WILL CRASH
    # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            print("Approx user location is known")
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            print("Approx user location is NOT known")
            user_longitude, user_latitude = locate_user()
    except:
        print("Location does not exist in the session")
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:10]
    
    # Looks for products in the selected bodega
    productos_en_bodegas = ProductosEnBodega.objects.all()
    try:
        if request.session['id_bodega'] == "Cercanas":
            print("id_bodega is Empty")
            result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0,peb_discount_status=True)[:20]
        elif request.session['id_bodega'] != "Cercanas":
            print("There is an id_bodega in session")
            result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0,peb_discount_status=True,peb_bodega__bd_ID=request.session['id_bodega'])[:20]
        else:
            print("id_bodega is None")
    except:
        print("id_bodega does not exist in the session")
        request.session['id_bodega'] = "Cercanas"
        request.session['bodega_name'] = "Cercanas"
        result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]
        print(str(":")+str(request.session['id_bodega'])+str(":"))

    # Bodega name to display
    if request.session['bodega_name'] == "Cercanas":
        id_bodega_text = "Seleccione su bodega"
    elif request.session['bodega_name'] != "Cercanas":
        id_bodega_text = request.session['bodega_name']
    else:
        print("What is this?")
    
    # Random shuffle the discount products
    temp = list(result_list)
    shuffle(temp)
    result_list = temp

    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/index.html", # where to find the specifix template
                  context={'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list, 
                           'user_location': user_location,
                           'shops': shops,
                           'id_bodega_text': id_bodega_text,
                           'STATIC_URL': STATIC_URL})

def embutidos(request):
    # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            user_longitude, user_latitude = locate_user()
    except:
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:10]
        
    # Looks for products in the selected bodega
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="embutidos").all()
    try:
        if request.session['id_bodega'] == "Cercanas":
            result_list = productos_en_bodegas.all()
        elif request.session['id_bodega'] != "Cercanas":
            result_list = productos_en_bodegas.filter(peb_bodega__bd_ID=request.session['id_bodega']).all()
        else:
            pass
    except:
        request.session['id_bodega'] = "Cercanas"
        request.session['bodega_name'] = "Cercanas"
        result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]

    # Bodega name to display
    if request.session['bodega_name'] == "Cercanas":
        id_bodega_text = "Seleccione su bodega"
    elif request.session['bodega_name'] != "Cercanas":
        id_bodega_text = request.session['bodega_name']
    else:
        print("What is this?")

    # Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(result_list, 12) # displayed products per page
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    result_count = paginator.count
    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/embutidos.html", # where to find the specifix template
                  context={'result_list': result_list,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'brands': brands,
                  'results': results,
                  'result_count': result_count,
                  'user_location': user_location,
                  'shops': shops,
                  'id_bodega_text': id_bodega_text,
                  'STATIC_URL': STATIC_URL})

def lacteos(request):
   # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            user_longitude, user_latitude = locate_user()
    except:
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:10]
        
    # Looks for products in the selected bodega
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="lacteos").all()
    try:
        if request.session['id_bodega'] == "Cercanas":
            result_list = productos_en_bodegas.all()
        elif request.session['id_bodega'] != "Cercanas":
            result_list = productos_en_bodegas.filter(peb_bodega__bd_ID=request.session['id_bodega']).all()
        else:
            pass
    except:
        request.session['id_bodega'] = "Cercanas"
        request.session['bodega_name'] = "Cercanas"
        result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]

    # Bodega name to display
    if request.session['bodega_name'] == "Cercanas":
        id_bodega_text = "Seleccione su bodega"
    elif request.session['bodega_name'] != "Cercanas":
        id_bodega_text = request.session['bodega_name']
    else:
        print("What is this?")

    # Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(result_list, 12) # displayed products per page
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    result_count = paginator.count
    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/lacteos.html", # where to find the specifix template
                  context={'result_list': result_list,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'brands': brands,
                  'results': results,
                  'result_count': result_count,
                  'user_location': user_location,
                  'shops': shops,
                  'id_bodega_text': id_bodega_text,
                  'STATIC_URL': STATIC_URL})

def abarrotes(request):
    # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            user_longitude, user_latitude = locate_user()
    except:
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:10]
        
    # Looks for products in the selected bodega
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="abarrotes").all()
    try:
        if request.session['id_bodega'] == "Cercanas":
            result_list = productos_en_bodegas.all()
        elif request.session['id_bodega'] != "Cercanas":
            result_list = productos_en_bodegas.filter(peb_bodega__bd_ID=request.session['id_bodega']).all()
        else:
            pass
    except:
        request.session['id_bodega'] = "Cercanas"
        request.session['bodega_name'] = "Cercanas"
        result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]

    # Bodega name to display
    if request.session['bodega_name'] == "Cercanas":
        id_bodega_text = "Seleccione su bodega"
    elif request.session['bodega_name'] != "Cercanas":
        id_bodega_text = request.session['bodega_name']
    else:
        print("What is this?")

    # Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(result_list, 12) # displayed products per page
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    result_count = paginator.count
    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/abarrotes.html", # where to find the specifix template
                  context={'result_list': result_list,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'brands': brands,
                  'results': results,
                  'result_count': result_count,
                  'user_location': user_location,
                  'shops': shops,
                  'id_bodega_text': id_bodega_text,
                  'STATIC_URL': STATIC_URL})

def limpieza(request):
    # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            user_longitude, user_latitude = locate_user()
    except:
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:10]
        
    # Looks for products in the selected bodega
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="limpieza").all()
    try:
        if request.session['id_bodega'] == "Cercanas":
            result_list = productos_en_bodegas.all()
        elif request.session['id_bodega'] != "Cercanas":
            result_list = productos_en_bodegas.filter(peb_bodega__bd_ID=request.session['id_bodega']).all()
        else:
            pass
    except:
        request.session['id_bodega'] = "Cercanas"
        request.session['bodega_name'] = "Cercanas"
        result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]

    # Bodega name to display
    if request.session['bodega_name'] == "Cercanas":
        id_bodega_text = "Seleccione su bodega"
    elif request.session['bodega_name'] != "Cercanas":
        id_bodega_text = request.session['bodega_name']
    else:
        print("What is this?")
    
    # Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(result_list, 12) # displayed products per page
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    result_count = paginator.count
    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/limpieza.html", # where to find the specifix template
                  context={'result_list': result_list,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'brands': brands,
                  'results': results,
                  'result_count': result_count,
                  'user_location': user_location,
                  'shops': shops,
                  'id_bodega_text': id_bodega_text,
                  'STATIC_URL': STATIC_URL})

def licores(request):
    # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            user_longitude, user_latitude = locate_user()
    except:
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:10]
        
    # Looks for products in the selected bodega
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="licores").all()
    try:
        if request.session['id_bodega'] == "Cercanas":
            result_list = productos_en_bodegas.all()
        elif request.session['id_bodega'] != "Cercanas":
            result_list = productos_en_bodegas.filter(peb_bodega__bd_ID=request.session['id_bodega']).all()
        else:
            pass
    except:
        request.session['id_bodega'] = "Cercanas"
        request.session['bodega_name'] = "Cercanas"
        result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]

    # Bodega name to display
    if request.session['bodega_name'] == "Cercanas":
        id_bodega_text = "Seleccione su bodega"
    elif request.session['bodega_name'] != "Cercanas":
        id_bodega_text = request.session['bodega_name']
    else:
        print("What is this?")

    # Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(result_list, 12) # displayed products per page
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    result_count = paginator.count
    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/licores.html", # where to find the specifix template
                  context={'result_list': result_list,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'brands': brands,
                  'results': results,
                  'result_count': result_count,
                  'user_location': user_location,
                  'shops': shops,
                  'id_bodega_text': id_bodega_text,
                  'STATIC_URL': STATIC_URL})

def vegetales(request):
    # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            user_longitude, user_latitude = locate_user()
    except:
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:10]
        
    # Looks for products in the selected bodega
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="vegetales").all()
    try:
        if request.session['id_bodega'] == "Cercanas":
            result_list = productos_en_bodegas.all()
        elif request.session['id_bodega'] != "Cercanas":
            result_list = productos_en_bodegas.filter(peb_bodega__bd_ID=request.session['id_bodega']).all()
        else:
            pass
    except:
        request.session['id_bodega'] = "Cercanas"
        request.session['bodega_name'] = "Cercanas"
        result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]

    # Bodega name to display
    if request.session['bodega_name'] == "Cercanas":
        id_bodega_text = "Seleccione su bodega"
    elif request.session['bodega_name'] != "Cercanas":
        id_bodega_text = request.session['bodega_name']
    else:
        print("What is this?")

    # Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(result_list, 12) # displayed products per page
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)
    result_count = paginator.count
    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/vegetales.html", # where to find the specifix template
                  context={'result_list': result_list,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'brands': brands,
                  'results': results,
                  'result_count': result_count,
                  'user_location': user_location,
                  'shops': shops,
                  'id_bodega_text': id_bodega_text,
                  'STATIC_URL': STATIC_URL})

def checkout(request):
    # Locate user and shops nearby.
    try:
        if request.session['user_longitude'] is not None and request.session['user_latitude'] is not None:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
        else:
            user_longitude, user_latitude = locate_user()
    except:
        user_longitude, user_latitude = locate_user()
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
    user_location = Point(user_longitude,user_latitude,srid=4326)

    # Check if user is logged in
    if request.user.is_authenticated:
        print("Cliente identificado")
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
    else:
        cliente = Cliente
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()
    # Look up for all stores with items in the shopping cart
    bodegas_en_cesta = []
    subtotal_bodegas = dict()
    for product in cart_list:
        # Check if bodega is already in the list
        if product.ci_product.peb_bodega in bodegas_en_cesta:
            if product.ci_product.peb_discount_status == True:
                subtotal_bodegas[str(product.ci_product.peb_bodega.bd_ruc)] += product.ci_product.peb_discount_price * product.ci_quantity
            else:
                subtotal_bodegas[str(product.ci_product.peb_bodega.bd_ruc)] += product.ci_product.peb_regular_price * product.ci_quantity
        else:
            bodegas_en_cesta.append(product.ci_product.peb_bodega)
            if product.ci_product.peb_discount_status == True:
                subtotal_bodegas.update({str(product.ci_product.peb_bodega.bd_ruc):product.ci_product.peb_discount_price * product.ci_quantity})
            else:
                subtotal_bodegas.update({str(product.ci_product.peb_bodega.bd_ruc):product.ci_product.peb_regular_price * product.ci_quantity})

    print(subtotal_bodegas)
    return render(request=request, # to reference request
                  template_name="main/checkout.html", # where to find the specifix template
                  context={'cliente': cliente,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'user_location': user_location,
                  'bodegas_en_cesta': bodegas_en_cesta,
                  'subtotal_bodegas': subtotal_bodegas,
                  'STATIC_URL': STATIC_URL})

def send_order_mail(orders_obj,usr_first,usr_last,usr_street,usr_geolocation,usr_email,usr_phone,usr_comments):
    # Retrieve all corresponding cart products
    result_list = OrderItem.objects.all().filter(oi_ID=orders_obj).all()

    # Organize all email context information
    bodegas_en_cesta = dict()
    bodega_names = dict()
    bodega_phones = dict()
    subtotal_bodegas = dict()
    for product in result_list:
        # Check if bodega is already in the dictionary
        if product.oi_id_bodega in bodegas_en_cesta:
            subtotal_bodegas[str(product.oi_id_bodega)] += float(product.oi_price)* float(product.oi_quantity)
        else:
            bodegas_en_cesta.update({str(product.oi_id_bodega):str(product.oi_ruc_bodega)})
            bodega_names.update({str(product.oi_id_bodega):str(product.oi_bodega_name)})
            bodega_phones.update({str(product.oi_id_bodega):str(product.oi_bodega_phone)})
            subtotal_bodegas.update({str(product.oi_id_bodega):float(product.oi_price) * float(product.oi_quantity) })

    # usr_geolocation with regex
    patterns = "([0-9.-]+)"
    match = re.findall(patterns, usr_geolocation) # Full match 0 is SRID, Full match 1 is Lng, Full match 2 is Lat
    lng = match[1]
    lat = match[2]

    # Get map image
    img_url = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-l+e7ab3c(%s,%s)/%s,%s,15/500x500?access_token=pk.eyJ1Ijoia3Bscm0iLCJhIjoiY2s4eGcybDhzMTAzbTNvb2trMzl4NGw1eSJ9.Jf4YQcLIbhHBWbpd7RPZaQ" % (lng,lat,lng,lat)
    response = requests.get(img_url)
    usr_map = ("data:" + response.headers['Content-Type'] + ";" + "base64," + str(base64.b64encode(response.content).decode("utf-8")))

    context = {
        'orders_obj': orders_obj, 
        'result_list': result_list,
        'bodegas_en_cesta': bodegas_en_cesta,
        'bodega_names': bodega_names,
        'bodega_phones': bodega_phones,
        'subtotal_bodegas': subtotal_bodegas,
        'usr_first': usr_first,
        'usr_last': usr_last,
        'usr_street': usr_street,
        'usr_geolocation': usr_geolocation,
        'usr_map': usr_map,
        'usr_email': usr_email,
        'usr_phone': usr_phone,
        'usr_comments': usr_comments
    }

    # Add email subject
    subject = "Orden de compra #"+str(orders_obj.ord_ID).zfill(8)

    # Image (logo) needs to be encoded before sending https://www.base64encode.net/base64-image-encoder
    html_content = render_to_string('main/customer_order_confirmation.html', context)
    email = EmailMultiAlternatives(subject=subject, from_email="hola@alimentos.pe",
                                to=[usr_email], body="text_body")
    email.attach_alternative(html_content, "text/html")
    #res = email.send()

    print("Email enviado")
    return HttpResponse('%s'%res)

def submit_checkout(request):
    if request.method== "POST" and request.is_ajax():
        # Stores variables in session
        cart_obj_id = request.POST['cart_obj_id']
        cart_obj = Cart.objects.all().filter(crt_ID=cart_obj_id).first()
        usr_first = request.POST['usr_first']
        usr_last = request.POST['usr_last']
        usr_street = request.POST['usr_street']
        usr_geolocation = request.POST['usr_geolocation']
        usr_email = request.POST['usr_email']
        usr_phone = request.POST['usr_phone']
        usr_comments = request.POST['usr_comments']

        # Creates a new order
        orders_obj = Orders.objects.create(ord_total_price=cart_obj.crt_total_price)
        
        # Saves user data if there is a user
        if request.user.is_authenticated:
            print("Cliente identificado")
            # Lines to update clients data           ord_user
            #cliente = Cliente.objects.all().filter(cl_user=request.user).first()
            #cliente.cl_bodega_ID = id_bodega
            #cliente.save()
        else:
            print("Usuario no identificado")
        
        # Get items from the basket
        cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

        # Crate a new bodegaorder for every bodega in the basket
        bodegas = dict()
        for item in cart_list:
            print("item.ci_product.peb_bodega.bd_ID: ",item.ci_product.peb_bodega.bd_ID)
            if item.ci_product.peb_bodega.bd_ID in bodegas: # Check for key in dict
                pass
            else:
                print("Nueva bodega en cesta")
                bodegaorders_obj = BodegaOrders.objects.create(bo_order=orders_obj,bo_bodega=item.ci_product.peb_bodega)
                bodegas.update({str(item.ci_product.peb_bodega.bd_ID): bodegaorders_obj})
        print(bodegas)
        
        # Create every order item
        for item in cart_list:
            order_item = OrderItem.objects.create(oi_ID=orders_obj)
            for bodega in bodegas.values():
                if bodega == item.ci_product.peb_bodega:
                    order_item.oi_bo_ID = bodega
                    print("Bodega añadida")
                    break
            order_item.oi_id_product = item.ci_product.peb_product.pa_ID
            order_item.oi_product = item.ci_product.peb_product.pa_product
            order_item.oi_quantity = item.ci_quantity
            order_item.oi_id_bodega = item.ci_product.peb_bodega.bd_ID
            order_item.oi_ruc_bodega = item.ci_product.peb_bodega.bd_ruc
            order_item.oi_bodega_name = item.ci_product.peb_bodega.bd_name
            order_item.oi_bodega_phone = item.ci_product.peb_bodega.bd_phone
            if item.ci_product.peb_discount_status:
                order_item.oi_price = item.ci_product.peb_discount_price
            else:
                order_item.oi_price = item.ci_product.peb_regular_price
            order_item.oi_prod_total = item.ci_quantity * order_item.oi_price
            order_item.save()

        send_order_mail(orders_obj,usr_first,usr_last,usr_street,usr_geolocation,usr_email,usr_phone,usr_comments)

    else:
        print("Not Ajax")
    return redirect('main:homepage')

def register(request): # CHANGE TO FORMVIEW BASED CLASS?
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        cl_form = ClientForm(request.POST)
        if form.is_valid() and cl_form.is_valid:
            user = form.save()
            client = cl_form.save(commit=False)
            client.cl_user = user
            client.cl_first_name = user.first_name
            client.cl_last_name = user.last_name
            client.cl_email = user.email
            cl_form.save(commit=True)
            username = user.username # normalize to a standard format
            # Messages are stored only once. When they are delivered, they also are deleted.
            messages.success(request,f"Cuenta creada exitosamente") # (request, exact message)
            auth_login(request, user)
            messages.info(request,f"Bienvenido: {username}")
            return redirect('main:homepage')
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            
    form = RegistrationForm() # Rerender form
    cl_form = ClientForm() # Rerender form
    return render(request, 'main/register.html', context={"form":form,"cl_form":cl_form})

def logout_request(request):
    auth_logout(request)
    messages.info(request, "Sessión cerrada. Vuelve pronto.")
    return redirect("main:homepage")

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.clean()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.info(request,f"Bienvenido: {username}")
                return redirect('main:homepage')
            else:
                messages.error(request,f"Usuario o contraseña incorrecta")
        # in case the form is invalid
        messages.error(request,f"Usuario o contraseña incorrecta")

    form = AuthenticationForm()
    return render(request, "main/login.html", {"form":form})

def session_cart_load_or_create(request):
    cart_obj, new_obj =  Cart.objects.new_or_get(request)
    return cart_obj, new_obj

def remove_cart(request):
    if request.method== "GET":
        print("a GET message arrived")
    if request.method== "POST":
        print("a POST message arrived")
        
    item_pk = request.POST.get('item_pk', None)
    #url_to_redirect = request.POST.get('url_to_redirect', None)

    item_obj = CartItem.objects.all().filter(pk=item_pk).first()
    cart_obj = Cart.objects.all().filter(crt_ID=item_obj.ci_cart_ID).first()
    
    cart_obj.crt_product.remove(item_obj.ci_product)
    cart_obj.crt_item.remove(item_obj)
    item_obj.delete()

    update_price(cart_obj)
    
    #data = {'exito':"exito"}
    #return JsonResponse(data)
    #print("redirecting to...")
    #print(url_to_redirect)
    #return redirect(url_to_redirect)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    #return HttpResponse("")

def cart_add(request):
    print("Entrando en el update!")
    # Retrieve on which object it was clicked
    product_pk = request.POST.get('product_id', None)
    if product_pk is not None:
        # Retrieves product and cart, and associates it to a cart_item
        product_obj = ProductosEnBodega.objects.all().filter(pk=product_pk).first()
        cart_obj, new_obj =  Cart.objects.new_or_get(request)
        # Check if the product is already in the cart
        print(product_obj)
        qs = Cart.objects.get_queryset().filter(pk=cart_obj.pk,crt_product=product_obj)
        if qs.count() == 1:
            print("Ya está en el coche")
            # INCREASE QUANTITY BY ONE
            cart_item = CartItem.objects.get_queryset().filter(ci_cart_ID=cart_obj.crt_ID,ci_product=product_obj).first()
            cart_item.ci_quantity += 1
            cart_item.save()
        else:
            print("Nuevo item en el coche!")
            cart_obj.crt_product.add(product_obj) # Add product to the cart
            cart_item = CartItem.objects.create(ci_cart_ID=cart_obj.crt_ID,ci_product=product_obj) # Create item
            cart_obj.crt_item.add(cart_item)

        update_price(cart_obj)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

def update_price(cart_obj):
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()
    total_price = 0
    for item in cart_list:
        if item.ci_product.peb_discount_status:
            total_price += item.ci_quantity * item.ci_product.peb_discount_price
        else:
            total_price += item.ci_quantity * item.ci_product.peb_regular_price
    cart_obj.crt_total_price = total_price
    cart_obj.save()
