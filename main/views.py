from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404 # to redirect the user
from .models import ProductosEnBodega, Cart, CartItem, Cliente, Bodega, Orders, BodegaOrders, OrderItem, BodegaDashboard, ProductosAprobados
from django.contrib.auth.models import User
from django.urls import reverse

from .forms import RegistrationForm, ClientForm, BodegaForm
from django.contrib.auth import update_session_auth_hash # to avoid the need to login again
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
# In django/contrib/auth/forms.py, in PasswordChangeForm change labels to spanish
# Old password -> Contraseña actual
# In django/contrib/auth/forms.py, in SetPasswordForm change labels to spanish
# New password -> Nueva contraseña
# New password confirmation -> Repita la nueva contraseña
# help_text=password_validation.password_validators_help_text_html(), -> Debe tener mínimo 8 caracteres entre números y letras.
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm
from django.contrib import messages # to send unique messages to the users

from itertools import chain
from random import shuffle

from django.conf import settings

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse

from django.core.mail import send_mail # simple email
from django.core.mail import EmailMultiAlternatives, EmailMessage # email with bcc
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from ipregistry import IpregistryClient, NoCache

from django.db.models import Q

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64
import requests
from PIL import Image
from io import BytesIO
from decimal import *
import re # regex
import unicodedata
import unidecode

# Encoding for digital invoice
import urllib.parse

import json
from django.http import JsonResponse

# Global variable Loads STATIC_URL
STATIC_URL = settings.STATIC_URL

def save_store_location(request):
    if request.method == "POST" and request.is_ajax():
        # Stores variables in session
        bodega_name = request.POST['bodega_name']
        request.session['bodega_name'] = bodega_name
        id_bodega = request.POST['id_bodega']
        request.session['id_bodega'] = id_bodega
        if request.user.is_authenticated:
#            print("Cliente identificado")
            cliente = Cliente.objects.all().filter(cl_user=request.user).first()
            cliente.cl_bodega_ID = id_bodega
            cliente.save()
        else:
            pass
#            print("Usuario no identificado")
    else:
        message = "Not Ajax"
    return HttpResponse("")

#def locate_user():
#    client = IpregistryClient("2cc3d6z6ct2weq", cache=NoCache())
#    ipInfo = client.lookup()
#    user_longitude = ipInfo.location['longitude']
#    user_latitude = ipInfo.location['latitude']
#    return user_longitude, user_latitude

# FUTURE IMPROVEMENT. IF ipregistry SERVER FAILS, OUR SITE WILL CRASH
def homepage(request):
    # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        #user_longitude, user_latitude = locate_user()
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Find shops nearby the user
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
    
    # Retrieve all products with discount from nearby shops
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = []
    for shop in shops:
        temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_discount_status=True,peb_discount_rate__lt=0,peb_discount_price__gt=0,peb_regular_price__gt=0)
        for product in temp:
            product_already_in_result_list = False
            for item in result_list:
                if item.peb_product.pa_ID == product.peb_product.pa_ID:
                    product_already_in_result_list = True
                    if item.peb_discount_price > product.peb_discount_price:
                        result_list.remove(item) # Removes existing more expensive item
                        result_list.append(product) # Adds new cheaper product
                    else:
                        break
            if product_already_in_result_list == False:
                result_list.append(product) # Add new product to the list
            else:
                product_already_in_result_list = False
    shuffle(result_list)

    return render(request=request,
                  template_name="main/index.html",
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list,
                           })

def embutidos(request):
    # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        #user_longitude, user_latitude = locate_user()
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Find shops nearby the user
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
    
    # Retrieve all products with discount from nearby shops
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = []
    for shop in shops:
        temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_product__pa_category="embutidos",peb_regular_price__gt=0)
        for product in temp:
            product_already_in_result_list = False
            for item in result_list:
                if item.peb_product.pa_ID == product.peb_product.pa_ID:
                    product_already_in_result_list = True
                    if item.peb_discount_price > product.peb_discount_price:
                        result_list.remove(item) # Removes existing more expensive item
                        result_list.append(product) # Adds new cheaper product
                    else:
                        break
            if product_already_in_result_list == False:
                result_list.append(product) # Add new product to the list
            else:
                product_already_in_result_list = False
    shuffle(result_list)

#    # Paginator
#    page = request.GET.get('page', 1)
#    paginator = Paginator(result_list, 12) # displayed products per page
#    try:
#        results = paginator.page(page)
#    except PageNotAnInteger:
#        results = paginator.page(1)
#    except EmptyPage:
#        results = paginator.page(paginator.num_pages)
#    result_count = paginator.count

    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    # Make alphabetical order
    sorted(brands)

    return render(request=request,
                  template_name="main/embutidos.html",
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list,
                           'brands': brands
# For paginator
#                            'results': results,
#                            'result_count': result_count,
                           })

def lacteos(request):
   # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        #user_longitude, user_latitude = locate_user()
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Find shops nearby the user
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
    
    # Retrieve all products with discount from nearby shops
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = []
    for shop in shops:
        temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_product__pa_category="lacteos",peb_regular_price__gt=0)
        for product in temp:
            product_already_in_result_list = False
            for item in result_list:
                if item.peb_product.pa_ID == product.peb_product.pa_ID:
                    product_already_in_result_list = True
                    if item.peb_discount_price > product.peb_discount_price:
                        result_list.remove(item) # Removes existing more expensive item
                        result_list.append(product) # Adds new cheaper product
                    else:
                        break
            if product_already_in_result_list == False:
                result_list.append(product) # Add new product to the list
            else:
                product_already_in_result_list = False
    shuffle(result_list)

#    # Paginator
#    page = request.GET.get('page', 1)
#    paginator = Paginator(result_list, 12) # displayed products per page
#    try:
#        results = paginator.page(page)
#    except PageNotAnInteger:
#        results = paginator.page(1)
#    except EmptyPage:
#        results = paginator.page(paginator.num_pages)
#    result_count = paginator.count

    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    # Make alphabetical order
    sorted(brands)

    return render(request=request,
                  template_name="main/lacteos.html",
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list,
                           'brands': brands
# For paginator
#                            'results': results,
#                            'result_count': result_count,
                           })

def abarrotes(request):
    # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        #user_longitude, user_latitude = locate_user()
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Find shops nearby the user
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
    
    # Retrieve all products with discount from nearby shops
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = []
    for shop in shops:
        temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_product__pa_category="abarrotes",peb_regular_price__gt=0)
        for product in temp:
            product_already_in_result_list = False
            for item in result_list:
                if item.peb_product.pa_ID == product.peb_product.pa_ID:
                    product_already_in_result_list = True
                    if item.peb_discount_price > product.peb_discount_price:
                        result_list.remove(item) # Removes existing more expensive item
                        result_list.append(product) # Adds new cheaper product
                    else:
                        break
            if product_already_in_result_list == False:
                result_list.append(product) # Add new product to the list
            else:
                product_already_in_result_list = False
    shuffle(result_list)

#    # Paginator
#    page = request.GET.get('page', 1)
#    paginator = Paginator(result_list, 12) # displayed products per page
#    try:
#        results = paginator.page(page)
#    except PageNotAnInteger:
#        results = paginator.page(1)
#    except EmptyPage:
#        results = paginator.page(paginator.num_pages)
#    result_count = paginator.count

    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    # Make alphabetical order
    sorted(brands)

    return render(request=request,
                  template_name="main/abarrotes.html",
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list,
                           'brands': brands
# For paginator
#                            'results': results,
#                            'result_count': result_count,
                           })

def limpieza(request):
    # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        #user_longitude, user_latitude = locate_user()
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Find shops nearby the user
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
    
    # Retrieve all products with discount from nearby shops
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = []
    for shop in shops:
        temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_product__pa_category="limpieza",peb_regular_price__gt=0)
        for product in temp:
            product_already_in_result_list = False
            for item in result_list:
                if item.peb_product.pa_ID == product.peb_product.pa_ID:
                    product_already_in_result_list = True
                    if item.peb_discount_price > product.peb_discount_price:
                        result_list.remove(item) # Removes existing more expensive item
                        result_list.append(product) # Adds new cheaper product
                    else:
                        break
            if product_already_in_result_list == False:
                result_list.append(product) # Add new product to the list
            else:
                product_already_in_result_list = False
    shuffle(result_list)

#    # Paginator
#    page = request.GET.get('page', 1)
#    paginator = Paginator(result_list, 12) # displayed products per page
#    try:
#        results = paginator.page(page)
#    except PageNotAnInteger:
#        results = paginator.page(1)
#    except EmptyPage:
#        results = paginator.page(paginator.num_pages)
#    result_count = paginator.count

    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    # Make alphabetical order
    sorted(brands)

    return render(request=request,
                  template_name="main/limpieza.html",
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list,
                           'brands': brands
# For paginator
#                            'results': results,
#                            'result_count': result_count,
                           })

def licores(request):
    # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        #user_longitude, user_latitude = locate_user()
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Find shops nearby the user
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
    
    # Retrieve all products with discount from nearby shops
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = []
    for shop in shops:
        temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_product__pa_category="licores",peb_regular_price__gt=0)
        for product in temp:
            product_already_in_result_list = False
            for item in result_list:
                if item.peb_product.pa_ID == product.peb_product.pa_ID:
                    product_already_in_result_list = True
                    if item.peb_discount_price > product.peb_discount_price:
                        result_list.remove(item) # Removes existing more expensive item
                        result_list.append(product) # Adds new cheaper product
                    else:
                        break
            if product_already_in_result_list == False:
                result_list.append(product) # Add new product to the list
            else:
                product_already_in_result_list = False
    shuffle(result_list)

#    # Paginator
#    page = request.GET.get('page', 1)
#    paginator = Paginator(result_list, 12) # displayed products per page
#    try:
#        results = paginator.page(page)
#    except PageNotAnInteger:
#        results = paginator.page(1)
#    except EmptyPage:
#        results = paginator.page(paginator.num_pages)
#    result_count = paginator.count

    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    # Make alphabetical order
    sorted(brands)

    return render(request=request,
                  template_name="main/licores.html",
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list,
                           'brands': brands
# For paginator
#                            'results': results,
#                            'result_count': result_count,
                           })

def vegetales(request):
    # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        #user_longitude, user_latitude = locate_user()
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Find shops nearby the user
    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
    
    # Retrieve all products with discount from nearby shops
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = []
    for shop in shops:
        temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_product__pa_category="vegetales",peb_regular_price__gt=0)
        for product in temp:
            product_already_in_result_list = False
            for item in result_list:
                if item.peb_product.pa_ID == product.peb_product.pa_ID:
                    product_already_in_result_list = True
                    if item.peb_discount_price > product.peb_discount_price:
                        result_list.remove(item) # Removes existing more expensive item
                        result_list.append(product) # Adds new cheaper product
                    else:
                        break
            if product_already_in_result_list == False:
                result_list.append(product) # Add new product to the list
            else:
                product_already_in_result_list = False
    shuffle(result_list)

#    # Paginator
#    page = request.GET.get('page', 1)
#    paginator = Paginator(result_list, 12) # displayed products per page
#    try:
#        results = paginator.page(page)
#    except PageNotAnInteger:
#        results = paginator.page(1)
#    except EmptyPage:
#        results = paginator.page(paginator.num_pages)
#    result_count = paginator.count

    # Lookup for all the brands
    brands = []
    for product in result_list:
        # Check if brand already in the list
        if product.peb_product.pa_brand in brands:
            pass
        else:
            brands.append(product.peb_product.pa_brand)
    # Make alphabetical order
    sorted(brands)

    return render(request=request,
                  template_name="main/vegetales.html",
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
                           'cart_list': cart_list,
                           'brands': brands
# For paginator
#                            'results': results,
#                            'result_count': result_count,
                           })

def see_search_results(request):
    if request.method == "GET":
        # Locate user and shops nearby.
        try:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
            introduction = False
            user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
        except:
            # Add guidance if it is the first time in the site
            request.session['introduction'] = True
            introduction = True
            # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
            user_longitude = -76.944204
            user_latitude = -12.109987
            #user_longitude, user_latitude = locate_user()
            user_location = Point(float(user_longitude),float(user_latitude),srid=4326)

        # Retrieves search_text
        search_text = request.GET.get('search-product',False)
        if search_text == False or search_text == "" or len(search_text) < 3: # If no valid search word
            return redirect('main:homepage')
        # Get search words
        search_words = search_text.split(" ")
        # Remove empty entries
        while('' in search_words):
            search_words.remove('')
    
        # Load or create cart
        cart_obj, new_obj = session_cart_load_or_create(request)
        # Load item list
        cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

        # Find shops nearby the user
        shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
        
        # Retrieve all products from nearby shops
        productos_en_bodegas = ProductosEnBodega.objects.all()
        result_list = []
        for shop in shops:
            temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_regular_price__gt=0)
            for product in temp:
                product_already_in_result_list = False
                for item in result_list:
                    if item.peb_product.pa_ID == product.peb_product.pa_ID:
                        product_already_in_result_list = True
                        if item.peb_discount_price > product.peb_discount_price:
                            result_list.remove(item) # Removes existing more expensive item
                            result_list.append(product) # Adds new cheaper product
                        else:
                            break
                if product_already_in_result_list == False:
                    result_list.append(product) # Add new product to the list
                else:
                    product_already_in_result_list = False
        shuffle(result_list)

        # Search for the best results
        result_dict = []
        for product in result_list:
            search_score = 0
            for i in range(0,len(search_words)):
                # Normalize string (eliminates accents)
                string_producto = str(product.peb_product.pa_product)
                string_producto = unidecode.unidecode(string_producto)
                search_w = search_words[i]
                search_w = unidecode.unidecode(search_w)
                # Look for matching word
                # usr_geolocation with regex
                patterns = '^(.*?(' + search_w + ')[^$]*)$'
                match = re.findall(patterns, string_producto, re.IGNORECASE) # Full match 0 is SRID, Full match 1 is Lng, Full match 2 is Lat
                search_score += len(match)

            if (search_score != 0):
                result_dict.append(product)
        result_list = result_dict

        # Sort items according to most suitable case
#        def comparator_price( tupleElem ):
#            #print("tupleElem[1][3]: ", tupleElem[1][3])
#            return tupleElem[1][3]
#        result_dict = sorted(result_dict.items(), key=comparator_price, reverse=True)

#        def comparator_len( tupleElem ):
#            print("tupleElem[1][1]: ", tupleElem[1][1])
#            return tupleElem[1][1]
#        bodegas_w_products_w_delivery.sort(key=comparator_len, reverse=True)

    #    # Paginator
    #    page = request.GET.get('page', 1)
    #    paginator = Paginator(result_list, 12) # displayed products per page
    #    try:
    #        results = paginator.page(page)
    #    except PageNotAnInteger:
    #        results = paginator.page(1)
    #    except EmptyPage:
    #        results = paginator.page(paginator.num_pages)
    #    result_count = paginator.count

        # Lookup for all the brands
        brands = []
        for product in result_list:
            # Check if brand already in the list
            if product.peb_product.pa_brand in brands:
                pass
            else:
                brands.append(product.peb_product.pa_brand)
        # Make alphabetical order
        sorted(brands)
        return render(request=request,
                    template_name="main/search_results.html",
                    context={'introduction': introduction,
                            'user_location': user_location,
                            'result_list': result_list,
                            'cart_obj': cart_obj,
                            'cart_list': cart_list,
                            'brands': brands
    # For paginator
    #                            'results': results,
    #                            'result_count': result_count,
                            })
    
    else: # if not GET method
        return redirect('main:homepage')

def search_cart_items_in_bodegas(shop,cart_list):
    items_in_bodega = []
    total_price_in_bodega = 0
    total_price_inc_delivery = 0
    delivery_price = 0
    for cart_item in cart_list:
        # Retrieve item if available
        try:
            item = get_object_or_404(ProductosEnBodega,peb_product__pa_ID=cart_item.ci_product.peb_product.pa_ID,peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_regular_price__gt=0)
            if item.peb_discount_status == True:
                total_price_in_bodega += item.peb_discount_price * cart_item.ci_quantity
                items_in_bodega.append([item, cart_item.ci_quantity, item.peb_discount_price*cart_item.ci_quantity])
            else:
                total_price_in_bodega += item.peb_regular_price * cart_item.ci_quantity
                items_in_bodega.append([item, cart_item.ci_quantity, item.peb_regular_price*cart_item.ci_quantity])
        except:
            pass
    if shop.bd_delivery == True: # If delivery is offered
        if shop.bd_delivery_type == False: # Always the same cost
            total_price_inc_delivery = Decimal(total_price_in_bodega) + shop.bd_delivery_cost
            delivery_price = shop.bd_delivery_cost
        else:
            if total_price_in_bodega >= shop.bd_delivery_free_starting_on: # Free starting on
                total_price_inc_delivery = total_price_in_bodega
                delivery_price = 0
            else: # Minimum amount for free delivery not reached
                total_price_inc_delivery = Decimal(total_price_in_bodega) + shop.bd_delivery_cost
                delivery_price = shop.bd_delivery_cost

    return total_price_inc_delivery, len(items_in_bodega), shop.bd_name, tuple(items_in_bodega), delivery_price

    # FOR FUTURE IMPLEMENTATION WHEN IN STORE PICK UP AVAILABLE
    #else:
    #    # Save on bodegas without delivery
    #    bodegas_w_products_no_delivery.update({
    #        str(shop.bd_ID): ( Decimal(total_price_in_bodega), len(items_in_bodega), tuple(items_in_bodega) )
    #    })

def checkout(request):
    # Locate user and shops nearby.
    try:
        user_longitude = request.session['user_longitude']
        user_latitude = request.session['user_latitude']
        introduction = False
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
    except:
        # Add guidance if it is the first time in the site
        request.session['introduction'] = True
        introduction = True
        # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
        user_longitude = -76.944204
        user_latitude = -12.109987
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)

    # Check if user is logged in
    if request.user.is_authenticated:
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
    else:
        cliente = Cliente
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    # Get bodegas close by
    bodegas_w_products_w_delivery = dict()
    #bodegas_w_products_no_delivery = dict()
    #print("cart_list: ", cart_list)
    try:
        shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
        for shop in shops:
            a,b,c,d,e = search_cart_items_in_bodegas(shop,cart_list)
            # Save on bodegas with delivery
            if b > 0: # Skip if no products are found at the bodega
                bodegas_w_products_w_delivery.update({
                    str(shop.bd_ID): ( a, b, c, d, e )
                })

        # bodegas_w_products_w_delivery CHANGES FROM TYPE DICT TO TYPE LIST AFTER SORTED
        # Cheapest on top
        def comparator_price( tupleElem ):
            #print("tupleElem[1][0]: ", tupleElem[1][0])
            return tupleElem[1][0]
        bodegas_w_products_w_delivery = sorted(bodegas_w_products_w_delivery.items(), key=comparator_price, reverse=False) # reverse=False -> Lowest to highest
        # Most products on top
        def comparator_len( tupleElem ):
            #print("tupleElem[1][1]: ", tupleElem[1][1])
            return tupleElem[1][1]
        bodegas_w_products_w_delivery.sort(key=comparator_len, reverse=True)

        # Shop selection results
        result_list = []
        for result in bodegas_w_products_w_delivery:
#            print(result[1][2], ": ", result[1][0],", ", result[1][1])
            # If all items are available at one store
            if result[1][1] == len(cart_list):
#                print("All items in store")
                result_list.append([result[1][0],result,1])
            # If items are available only buying at two shops
            else:
#                print("Missing items in ",result[1][2])
                # List all missing items
                missing_items_list = cart_list
                for item, qty, st in list(result[1][3]):
                    missing_items_list = missing_items_list.filter(~Q(ci_product__peb_product__pa_ID=item.peb_product.pa_ID))
                # Search again in all shops for the missing items
                second_bodega_w_products_w_delivery = dict()
                for shop in shops:
                    a,b,c,d,e = search_cart_items_in_bodegas(shop,missing_items_list)
                    # Save on bodegas with delivery
                    second_bodega_w_products_w_delivery.update({
                        str(shop.bd_ID): ( a, b, c, d, e )
                    })
                second_bodega_w_products_w_delivery = sorted(second_bodega_w_products_w_delivery.items(), key=comparator_price, reverse=False)
                second_bodega_w_products_w_delivery.sort(key=comparator_len, reverse=True)
                result_list.append([Decimal(result[1][0])+second_bodega_w_products_w_delivery[0][1][0],result,second_bodega_w_products_w_delivery[0]])

    except:
#        print("There are no stores in your surounding")
        pass

    # Look up for all stores with items in the shopping cart
#    bodegas_en_cesta = []
#    subtotal_bodegas = dict()
#    for product in cart_list:
#        # Check if bodega is already in the list
#        if product.ci_product.peb_bodega in bodegas_en_cesta:
#            if product.ci_product.peb_discount_status == True:
#                subtotal_bodegas[str(product.ci_product.peb_bodega.bd_ruc)] += product.ci_product.peb_discount_price * product.ci_quantity
#            else:
#                subtotal_bodegas[str(product.ci_product.peb_bodega.bd_ruc)] += product.ci_product.peb_regular_price * product.ci_quantity
#        else:
#            bodegas_en_cesta.append(product.ci_product.peb_bodega)
#            if product.ci_product.peb_discount_status == True:
#                subtotal_bodegas.update({str(product.ci_product.peb_bodega.bd_ruc):product.ci_product.peb_discount_price * product.ci_quantity})
#            else:
#                subtotal_bodegas.update({str(product.ci_product.peb_bodega.bd_ruc):product.ci_product.peb_regular_price * product.ci_quantity})

#    print(subtotal_bodegas)
    return render(request=request, # to reference request
                  template_name="main/checkout.html", # where to find the specifix template
                  context={'introduction': introduction,
                           'user_location': user_location,
                           'result_list': result_list,
                           'cart_obj': cart_obj,
#                           'cliente': cliente,
#                  'cart_list': cart_list,
#                  'user_location': user_location,
#                  'bodegas_en_cesta': bodegas_en_cesta,
#                  'subtotal_bodegas': subtotal_bodegas,
#                  'STATIC_URL': STATIC_URL
                  })

def send_order_mail(orders_obj,bodegas,usr_first,usr_last,usr_street,usr_geolocation,usr_email,usr_phone,usr_comments):
    # Retrieve all corresponding cart products
    result_list = OrderItem.objects.all().filter(oi_ID=orders_obj).all()

    # Organize all email context information
    bodegas_en_cesta = dict()
    bodega_names = dict()
    bodega_phones = dict()
    bodega_delivery = dict()
    subtotal_bodegas = dict()
    for product in result_list:
        # Check if bodega is already in the dictionary
        if product.oi_id_bodega in bodegas_en_cesta:
            pass
        else:
            bodegas_en_cesta.update({str(product.oi_id_bodega):str(product.oi_ruc_bodega)})
            bodega_names.update({str(product.oi_id_bodega):str(product.oi_bodega_name)})
            bodega_phones.update({str(product.oi_id_bodega):str(product.oi_bodega_phone)})
            bodega_delivery.update({str(product.oi_id_bodega):bodegas[str(product.oi_id_bodega)].bo_delivery })
            subtotal_bodegas.update({str(product.oi_id_bodega):bodegas[str(product.oi_id_bodega)].bo_total_price })

    # usr_geolocation with regex
    patterns = "([0-9.-]+)"
    match = re.findall(patterns, usr_geolocation) # Full match 0 is SRID, Full match 1 is Lng, Full match 2 is Lat
    lng = match[1]
    lat = match[2]

    # Get map image
    img_url = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/pin-l+e7ab3c(%s,%s)/%s,%s,15/500x500?access_token=pk.eyJ1Ijoia3Bscm0iLCJhIjoiY2s4eGcybDhzMTAzbTNvb2trMzl4NGw1eSJ9.Jf4YQcLIbhHBWbpd7RPZaQ" % (lng,lat,lng,lat)
    usr_map = img_url
    # Get google search location
    map_url = "https://maps.google.com/maps?q=loc:%s,%s" % (lat,lng)
#    response = requests.get(img_url)
#    usr_map = ("data:" + response.headers['Content-Type'] + ";" + "base64," + str(base64.b64encode(response.content).decode("utf-8")))
#    # Img to PNG (potential improvement to save it directly to PNG without making it first base64)
#    temp = base64.b64encode(response.content).decode("utf-8")
#    im_png = Image.open(BytesIO(base64.b64decode(temp)))
#    im_png.save('image.png', 'PNG')
#    usr_map = im_png

    context = {
        'orders_obj': orders_obj, 
        'result_list': result_list,
        'bodegas_en_cesta': bodegas_en_cesta,
        'bodega_names': bodega_names,
        'bodega_phones': bodega_phones,
        'bodega_delivery': bodega_delivery,
        'subtotal_bodegas': subtotal_bodegas,
        'usr_first': usr_first,
        'usr_last': usr_last,
        'usr_street': usr_street,
        'usr_geolocation': usr_geolocation,
        'usr_map': usr_map,
        'map_url': map_url,
        'usr_email': usr_email,
        'usr_phone': usr_phone,
        'usr_comments': usr_comments
    }

    # Add email subject
    subject = "Orden de compra #"+str(orders_obj.ord_ID).zfill(8)

    # Image (logo) needs to be encoded before sending https://www.base64encode.net/base64-image-encoder
    html_content = render_to_string('main/customer_order_confirmation.html', context)
    plain_message = strip_tags(html_content)

    # Envio de email al cliente
    send_mail(subject=subject, message=plain_message, from_email="Alimentos.pe <hola@alimentos.pe>",
                recipient_list=[usr_email], html_message=html_content, fail_silently=False)

    # Send mail to bodegas
    for bodega_id in bodegas:
        # Get the bodega object from bodega string
        bodega_obj = get_object_or_404(Bodega,bd_ID=bodega_id)
        # Retrieve all corresponding cart products
        result_list = OrderItem.objects.all().filter(oi_ID=orders_obj,oi_bo_ID__bo_bodega=bodega_obj).all()
        bodegaorder_obj = get_object_or_404(BodegaOrders,bo_order=orders_obj,bo_bodega=bodega_obj)
        context = {
            'orders_obj': orders_obj,
            'bodega_obj': bodega_obj,
            'bodegaorder_obj': bodegaorder_obj,
            'result_list': result_list,
            'usr_first': usr_first,
            'usr_last': usr_last,
            'usr_street': usr_street,
            'usr_geolocation': usr_geolocation,
            'usr_map': usr_map,
            'map_url': map_url,
            'usr_email': usr_email,
            'usr_phone': usr_phone,
            'usr_comments': usr_comments
        }
        # Add email subject
        subject = "Orden de compra #"+str(orders_obj.ord_ID).zfill(8)

        # Image (logo) needs to be encoded before sending https://www.base64encode.net/base64-image-encoder
        html_content = render_to_string('main/bodega_order_confirmation.html', context)
        plain_message = strip_tags(html_content)

        # Envio de email a bodegas
        send_mail(subject=subject, message=plain_message, from_email="Alimentos.pe <hola@alimentos.pe>",
                    recipient_list=[bodega_obj.bd_email], html_message=html_content, fail_silently=False)

def submit_checkout(request):
    if request.method== "POST" and request.is_ajax():
        # Saves user data if there is a user
        if request.user.is_authenticated:
            pass
#            print("Cliente identificado")
            # Lines to update clients data           ord_user
            #cliente = Cliente.objects.all().filter(cl_user=request.user).first()
            #cliente.cl_bodega_ID = id_bodega
            #cliente.save()
        else:
            pass
#            print("Usuario no identificado")

        # Retrieves products to buy
        products_to_buy = request.POST.get('products_to_buy',False)
        if products_to_buy != False:
            products_to_buy = json.loads(products_to_buy)
        
        # Retrieves user information
        cart_obj_ID = request.POST['cart_obj_ID']
        cart_obj = Cart.objects.all().filter(crt_ID=cart_obj_ID).first()
        usr_first = request.POST['usr_first']
        usr_last = request.POST['usr_last']
        usr_street = request.POST['usr_street']
        usr_geolocation = request.POST['usr_geolocation']
        usr_email = request.POST['usr_email']
        usr_phone = request.POST['usr_phone']
        usr_comments = request.POST['usr_comments']

        # Get the shopping list
        shopping_list = []
        for product in products_to_buy:
            item = get_object_or_404(ProductosEnBodega,peb_ID=str(product['key']))
            shopping_list.append(item)
        
        # Update cart and cart items according to the shopping list
        cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()
        for item in cart_list:
            for shopping_item in shopping_list:
                if str(item.ci_product.peb_product.pa_ID) == str(shopping_item.peb_product.pa_ID):
                    cart_obj.crt_product.remove(item.ci_product)
                    cart_obj.crt_product.add(shopping_item)
                    item.ci_product = shopping_item
                    item.save()
                    shopping_list.remove(shopping_item)
                    break
                else:
                    continue
        # Reload cart_list with the products updated
        cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()
        update_price(cart_obj)
        
        # Check for not available items
        not_available_items = []
        for item in cart_list:
            if item.ci_product.peb_status == False or item.ci_product.peb_product.pa_status == False:
                not_available_items.append( str(item.ci_product.peb_product.pa_product) )
                peb = ProductosEnBodega.objects.all().filter(peb_ID=item.ci_product.peb_ID).all().first()
                cart_obj.crt_product.remove(peb) # remove crt_product
                cart_obj.crt_item.remove(item) # remove crt_item
                item.delete()
                update_price(cart_obj)
        not_available_items = tuple(not_available_items)
        # Reload items from the basket after purging not available items
        cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

        # SEND JSON RESPONSE!!!!!!!!!!!
        if cart_obj.crt_total_price == 0: # If cart price is zero
            response_data = {"error": not_available_items }
            return JsonResponse(response_data, status=400)
        # In case shopping cart is not empty
        elif cart_obj.crt_total_price > 0: # If cart price is larger than zero
            # Creates a new order
#            orders_obj = Orders.objects.create(ord_total_price=cart_obj.crt_total_price)
            orders_obj = Orders.objects.create()

            # Crate a new bodegaorder for every bodega in the basket
            bodegas = dict()
            for item in cart_list:
                if str(item.ci_product.peb_bodega.bd_ID) in bodegas: # Check for key in dict
                    pass
                else:
                    bodegaorders_obj = BodegaOrders.objects.create(bo_order=orders_obj,bo_bodega=item.ci_product.peb_bodega)
                    bodegas.update({str(item.ci_product.peb_bodega.bd_ID): bodegaorders_obj})
            
            # Create every order item
            for item in cart_list:
                order_item = OrderItem.objects.create(oi_ID=orders_obj)
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
                order_item.oi_prod_total = round(item.ci_quantity * order_item.oi_price, 2)
                # Adds bodegaorders_obj to order_item
                for bodega in bodegas:
                    if str(bodega) == str(item.ci_product.peb_bodega.bd_ID):
                        order_item.oi_bo_ID = bodegas[str(bodega)]
                        # Updates bodega order total price
                        bodegas[str(bodega)].bo_total_price += order_item.oi_prod_total
                        # Updates bodega order delivery price
                        if item.ci_product.peb_bodega.bd_delivery == True: # If delivery is offered
                            if item.ci_product.peb_bodega.bd_delivery_type == False: # Always the same cost
                                bodegas[str(bodega)].bo_delivery = item.ci_product.peb_bodega.bd_delivery_cost
                            else:
                                if bodegas[str(bodega)].bo_total_price >= item.ci_product.peb_bodega.bd_delivery_free_starting_on: # Free starting on
                                    bodegas[str(bodega)].bo_delivery = 0
                                else: # Minimum amount for free delivery not reached
                                    bodegas[str(bodega)].bo_delivery = item.ci_product.peb_bodega.bd_delivery_cost
                        bodegas[str(bodega)].save()
                        break
                order_item.save()
            # Update bodega orders total price including final delivery cost
            total_price = 0
            for bodega in bodegas:
                bodegas[str(bodega)].bo_total_price =  Decimal(bodegas[str(bodega)].bo_total_price) + bodegas[str(bodega)].bo_delivery
                total_price = Decimal(total_price) + bodegas[str(bodega)].bo_total_price
                bodegas[str(bodega)].save()
            # Update order including final delivery cost
            orders_obj.ord_total_price = total_price
            orders_obj.save()

            # Send email to client and bodegas
            send_order_mail(orders_obj,bodegas,usr_first,usr_last,usr_street,usr_geolocation,usr_email,usr_phone,usr_comments)

            # Delete current cart and its associated items before submitting
            cart_obj.delete()
            for item in cart_list:
                item.delete()

            # Send JsonResponse
            response_data = {"success": not_available_items, "buy_order": orders_obj.ord_ID }
            return JsonResponse(response_data, status=200)
        else: # If price is less than zero
            return JsonResponse({"error": "Invalid cart value"}, status=400)
    
    # In case is not post neither ajax
    else:
        return JsonResponse({"error": "something went wrong"}, status=400)

def pay(request, order_id=0):
    if order_id != 0:
        order_obj = get_object_or_404(Orders,ord_ID=order_id)
        context = {
            'order_obj': order_obj,
        }

    return render(request=request,template_name="main/pay.html",context=context)

def payment_method(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieves payment method. 0:Error,1:Cash,2:Yape
        payment_method = request.POST.get('payment_method',False)
        order_id = request.POST.get('order_id',False)
        if payment_method != False and order_id != False:
            orders_obj = get_object_or_404(Orders,ord_ID=order_id)
            if payment_method == 1:
                orders_obj.ord_payment_method = 1
            elif payment_method == 2:
                orders_obj.ord_payment_method = 2
            else:
                orders_obj.ord_payment_method = 0
            orders_obj.save()
            return JsonResponse({"success": "Laika"}, status=200)
        return JsonResponse({"error": "Something went wrong"}, status=400)
    return JsonResponse({"error": "Something went wrong"}, status=400)

def validate_payment(request):
    print("in validate_payment...")
    if request.method == "POST" and request.is_ajax():
        # Retrieve token
        token = request.POST.get('token',False)
        order_id = request.POST.get('order_id',False)
        if token != False and order_id != False: # Compares public and private tokens
            private_key = 'N1FqhVa4eppK6Wfps89NiR1O55IVLjtVE7FZ'
            API_url = "http://maximo-api.herokuapp.com/api/v1/guest-payment/generate-payment"
            response = requests.post(API_url, data = {"private_key": private_key, "guest_payment_token": token})
            print("response.status_code: ", response.status_code)
            print("response.status_code: ", response)
            if response.status_code == 201:
                print ('OK!')
                orders_obj = get_object_or_404(Orders,ord_ID=order_id)
                #send_invoice(orders_obj) # Generates invoice for SUNAT
                orders_obj.ord_paid = True
                orders_obj.save()
                return JsonResponse({"success": "Laika"}, status=200)
            else:
                print ('NOT OK!')
                return JsonResponse({"error": "Missing token"}, status=400)
        else:
            return JsonResponse({"error": "Missing token"}, status=400)
    return JsonResponse({"error": "Something went wrong"}, status=400)

def send_invoice(orders_obj):
    # client_id needs to be change from SOL Menu
    dia = date.today().year
    mes = date.today().month
    anio = date.today().day
    orders_obj.ord_taxes = orders_obj.ord_total_price * 0.18
    orders_obj.save()
    #OrderItem = get_object_or_404(OrderItem,oi_ID=orders_obj)
    settings =  {
                    "async": "true",
                    "crossDomain": "true",
                    "url": "http://demo.mifact.net.pe/api/invoiceService.svc/SendInvoice",
                    "method": "POST",
                    "headers":  {
                        "content-type": "application/json",
                        "cache-control": "no-cache",
                        "postman-token": "05d67f93-91db-85ae-fc06-c565a92c4181"
                    },
                    "processData": "false",
                    "data": {
                        "TOKEN":"gN8zNRBV+/FVxTLwdaZx0w==",
                        "COD_TIP_NIF_EMIS": "6",
                        "NUM_NIF_EMIS": "20600035674",
                        "NOM_RZN_SOC_EMIS": "CR INMOBILIARIA NETWORKER S.A.C.",
                        "NOM_COMER_EMIS": "ALIMENTOS PUNTO PE",
                        "COD_UBI_EMIS": "150114",
                        "TXT_DMCL_FISC_EMIS": "CAL.BADAJOZ MZA. E LOTE. 11 URB. LA CAPILLA (SUPER MANZANA U3) LIMA - LIMA - LA MOLINA",
                        "COD_TIP_NIF_RECP": "0",
                        "NUM_NIF_RECP": "00000000",
                        "NOM_RZN_SOC_RECP": "CLIENTE SIN NOMBRE",
                        "TXT_DMCL_FISC_RECEP": "SIN DIRECCION",
                        "FEC_EMIS": str(anio)+"-"+str(mes)+"-"+str(dia),
                        "FEC_VENCIMIENTO": str(anio)+"-"+str(mes)+"-"+str(dia),
                        "COD_TIP_CPE": "03",
                        "NUM_SERIE_CPE": "B002",
                        "NUM_CORRE_CPE": str(orders_obj.ord_ID).zfill(8),
                        "COD_MND": "PEN",
                        "MailEnvio": "hola@alimentos.pe",
                        "COD_PRCD_CARGA": "001",
                        "MNT_TOT_GRAVADO": str(orders_obj.ord_total_price - orders_obj.ord_taxes), 
                        "MNT_TOT_TRIB_IGV": str(orders_obj.ord_taxes), 
                        "MNT_TOT": str(orders_obj.ord_total_price), 
                        "ENVIAR_A_SUNAT": "true",
                        "RETORNA_XML_ENVIO": "true",
                        "RETORNA_XML_CDR": "false",
                        "RETORNA_PDF": "false",
                        "COD_FORM_IMPR":"001",
                        "TXT_VERS_UBL":"2.1",
                        "TXT_VERS_ESTRUCT_UBL":"2.0",
                        "COD_ANEXO_EMIS":"0000",
                        "COD_TIP_OPE_SUNAT": "0101",
                        "items": [{
                            "COD_ITEM": "BCF-RR01",
                            "COD_UNID_ITEM": "NIU",
                            "CANT_UNID_ITEM": "1",
                            "VAL_UNIT_ITEM": "500",      
                            "PRC_VTA_UNIT_ITEM": "590",
                            "VAL_VTA_ITEM": "500",
                            "MNT_BRUTO": "500.00",
                            "MNT_PV_ITEM": "590",
                            "COD_TIP_PRC_VTA": "01",
                            "COD_TIP_AFECT_IGV_ITEM":"10",
                            "COD_TRIB_IGV_ITEM": "1000",
                            "POR_IGV_ITEM": "18",
                            "MNT_IGV_ITEM": "90",      
                            "TXT_DESC_ITEM": "AUTO TOYOTA YARIS 2018",                  
                            "DET_VAL_ADIC01": "dato adiciona al item: AÑO DE FABRICACION 2018  ",
                            "DET_VAL_ADIC02": "VERSION FULLL",
                            "DET_VAL_ADIC03": "COLOR:GRIS",
                            "DET_VAL_ADIC04": "NRO. MOTOR: JP8383838HYHYJJDD"
                        },
                        {
                            "COD_ITEM": "BCF-RR02",
                            "COD_UNID_ITEM": "NIU",
                            "CANT_UNID_ITEM": "1",
                            "VAL_UNIT_ITEM": "500",      
                            "PRC_VTA_UNIT_ITEM": "590",
                            "VAL_VTA_ITEM": "500",
                            "MNT_BRUTO": "500.00",
                            "MNT_PV_ITEM": "590",
                            "COD_TIP_PRC_VTA": "01",
                            "COD_TIP_AFECT_IGV_ITEM":"10",
                            "COD_TRIB_IGV_ITEM": "1000",
                            "POR_IGV_ITEM": "18",
                            "MNT_IGV_ITEM": "90",  
                            "TXT_DESC_ITEM": "DETALLE DEL PRODUCTO 2"
                        }]
                    }
                }
    API_url = "http://demo.mifact.net.pe/api/invoiceService.svc/SendInvoice"
    response = requests.post(API_url, data = settings)
    print("response.status_code: ", response.status_code)
#    data = {'grant_type': 'client_credentials','scope': 'https://api.sunat.gob.pe/v1/contribuyente/contribuyentes','client_id': 'client_id','client_secret': 'client_secret'}
#    response = requests.post(url = "https://api-seguridad.sunat.gob.pe/v1/clientesextranet/client_id/oauth2/token/",
#                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
#                                data=data)
#    print("access_token: ", response.access_token)
#    print("token_type: ", response.token_type)
#    print("expires_in: ", response.expires_in)

def payment(request, order_id=0):
    if order_id != 0:
        order_obj = get_object_or_404(Orders,ord_ID=order_id)
        context = {
            'order_obj': order_obj
        }
    return render(request=request,template_name="main/payment.html",context=context)

def registro(request):
    if request.user.is_authenticated:
        return redirect('main:homepage')
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
    cl_form = ClientForm()
    return render(request, 'main/registro-cliente.html', context={"form":form,"cl_form":cl_form})

def registroBodega(request):
    if request.user.is_authenticated:
        return redirect('main:homepage')
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        cl_form = ClientForm(request.POST)
        bd_form = BodegaForm(request.POST)
        if form.is_valid():
            if cl_form.is_valid and bd_form.is_valid:
                user = form.save()
                client = cl_form.save(commit=False)
                client.cl_user = user
                client.cl_first_name = user.first_name
                client.cl_last_name = user.last_name
                client.cl_email = user.email
                client.cl_is_bodega = True
                client.cl_terms = True
                cl_form.save(commit=True)
                bodega = bd_form.save(commit=False)
                bodega.bd_user = client
                bodega.bd_is_active = True # Active from beginning
                bodega.bd_email = client.cl_email
                bodega.bd_phone = client.cl_phone
                bodega.bd_delivery = True
                bodega = bd_form.save(commit=True)
                client.cl_default_bodega = str(bodega.bd_ID)
                cl_form.save(commit=True)
                username = user.username # normalize to a standard format
                # Messages are stored only once. When they are delivered, they also are deleted.
                messages.success(request,f"Cuenta creada exitosamente") # (request, exact message)
                auth_login(request, user)
                messages.info(request,f"Bienvenido: {username}")

                # Send welcome message
                context = {
                    'client': client
                }

                # Add email subject
                subject = "Te damos la bienvenida "+str(client.cl_first_name)

                # HTML content
                html_content = render_to_string('main/bodega_welcome.html', context)
                plain_message = strip_tags(html_content)

                # Envio de email de bienvenida al cliente
                email = EmailMultiAlternatives(subject=subject, body=plain_message, from_email="Alimentos.pe <hola@alimentos.pe>", to=[client.cl_email], bcc=["hola@alimentos.pe"])
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)

                return redirect('main:homepage')
            else:
                for msg in form.error_messages:
                    messages.error(request, f"{msg}: {form.error_messages[msg]}")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            
    form = RegistrationForm()
    cl_form = ClientForm()
    bd_form = BodegaForm()
    return render(request, 'main/registro-bodega.html', context={"form":form,"cl_form":cl_form,"bd_form":bd_form})

def logout_request(request):
    auth_logout(request)
    messages.info(request, "Sessión cerrada. Vuelve pronto.")
    return redirect("main:homepage")

def change_password_request(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            pc_form = PasswordChangeForm(request.user, request.POST)
            if pc_form.is_valid():
                user = pc_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Su contraseña fue actualizada!')
                return redirect("main:homepage")
            else:
                messages.error(request, 'Error: contraseña actual incorrecta.')
                return redirect("main:change_password_request")
        else:
            pc_form = PasswordChangeForm(request.user)
            return render(request, 'main/password-change.html', context={"pc_form":pc_form})
    else: # if user is not authenticated
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

def remove_cart_item(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieve item_pk
        item_pk = request.POST.get('product_id',False)
        item_pa_ID = request.POST.get('item_pa_ID',False)
        cart_obj_ID = request.POST.get('cart_obj_ID',False)
        if item_pk != False:
            item_pk = json.loads(item_pk)
            
            # Retrieve cart and cart object
            item_obj = CartItem.objects.all().filter(pk=item_pk).first()
            cart_obj = Cart.objects.all().filter(crt_ID=item_obj.ci_cart_ID).first()
            
            #Remove item
            cart_obj.crt_product.remove(item_obj.ci_product)
            cart_obj.crt_item.remove(item_obj)
            item_obj.delete()

            # Update cart price
            update_price(cart_obj)
            return JsonResponse({"success": str(cart_obj.crt_total_price)}, status=200)
        elif item_pa_ID != False and cart_obj_ID != False:
            # Retrieve cart and cart object
            item_obj = CartItem.objects.all().filter(ci_cart_ID=cart_obj_ID,ci_product__peb_product__pa_ID=item_pa_ID).first()
            cart_obj = Cart.objects.all().filter(crt_ID=cart_obj_ID).first()
            
            #Remove item
            cart_obj.crt_product.remove(item_obj.ci_product)
            cart_obj.crt_item.remove(item_obj)
            item_obj.delete()

            # Update cart price
            update_price(cart_obj)
            return JsonResponse({"success": ""}, status=200)
        else:
            return JsonResponse({"error": ""}, status=400)
    else:
        return JsonResponse({"error": ""}, status=400)

def increase_quantity_cart_item(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieve item_pk
        item_pk = request.POST.get('product_id',False)
        if item_pk != False:
            item_pk = json.loads(item_pk)
            
            # Retrieve cart and cart object
            item_obj = CartItem.objects.all().filter(pk=item_pk).first()
            cart_obj = Cart.objects.all().filter(crt_ID=item_obj.ci_cart_ID).first()
            
            # Increase item quantity
            item_obj.ci_quantity += 1
            item_obj.save()
            
            # Update cart price
            update_price(cart_obj)

            return JsonResponse({"success": {"total_price": str(cart_obj.crt_total_price), "quantity": str(item_obj.ci_quantity) }}, status=200)
        else:
            return JsonResponse({"error": ""}, status=400)
    else:
        return JsonResponse({"error": ""}, status=400)

def reduce_quantity_cart_item(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieve item_pk
        item_pk = request.POST.get('product_id',False)
        if item_pk != False:
            item_pk = json.loads(item_pk)
            
            # Retrieve cart and cart object
            item_obj = CartItem.objects.all().filter(pk=item_pk).first()
            cart_obj = Cart.objects.all().filter(crt_ID=item_obj.ci_cart_ID).first()
            
            # Reduce item quantity
            if item_obj.ci_quantity > 1:
                item_obj.ci_quantity -= 1
                item_obj.save()
            else:
                pass
            
            # Update cart price
            update_price(cart_obj)

            return JsonResponse({"success": {"total_price": str(cart_obj.crt_total_price), "quantity": str(item_obj.ci_quantity) }}, status=200)
        else:
            return JsonResponse({"error": ""}, status=400)
    else:
        return JsonResponse({"error": ""}, status=400)

def cart_add(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieve on which object it was clicked
        product_pk = request.POST.get('product_id',False)
        if product_pk != False:
            # Retrieves product and cart, and associates it to a cart_item
            product_obj = ProductosEnBodega.objects.all().filter(pk=product_pk).first()
            cart_obj, new_obj =  Cart.objects.new_or_get(request)
            # Check if the product is already in the cart
            qs = Cart.objects.get_queryset().filter(pk=cart_obj.pk,crt_product=product_obj)
            if qs.count() == 1:
                # Increase quantity
                cart_item = CartItem.objects.get_queryset().filter(ci_cart_ID=cart_obj.crt_ID,ci_product=product_obj).first()
                cart_item.ci_quantity += 1
                cart_item.save()
                new_added = False # Marker for responsive cart add to tell that this item was already in the cart
            else:
                # Add product to the cart
                cart_obj.crt_product.add(product_obj)
                cart_item = CartItem.objects.create(ci_cart_ID=cart_obj.crt_ID,ci_product=product_obj) # Create item
                cart_obj.crt_item.add(cart_item)
                new_added = True

            update_price(cart_obj)
            if product_obj.peb_discount_status == True:
                price = product_obj.peb_discount_price
            else:
                price = product_obj.peb_regular_price
            return JsonResponse({"success": {   "total_price": str(cart_obj.crt_total_price), 
                                                "quantity": str(cart_item.ci_quantity),
                                                "product_pk": str(cart_item.pk),
                                                "product": str(product_obj.peb_product.pa_product),
                                                "pa_image_url": str(product_obj.peb_product.pa_image.url),
                                                "price": str(price),
                                                "new_added": str(new_added)
                                                 }}, status=200)
        else:
            return JsonResponse({"error": ""}, status=400)
    else:
        return JsonResponse({"error": ""}, status=400)

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






#############################################################################
###############################   DASHBOARD   ###############################
#############################################################################

#@login_required(login_url='/accounts/login/')
def dashboard(request):
    if request.user.is_authenticated:
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        # Render only if it's bodega
        # To avoid any rendering or calculation if it's not a bodega
        if cliente.cl_is_bodega == False:
            return HttpResponseRedirect(reverse('main:homepage'))
        ####################################################################################
        ################################### PAGE CONTENT ###################################
        # Search for client's bodega and it's data
        bodega = Bodega.objects.all().filter(bd_ID=cliente.cl_default_bodega).first()
        BodegaDashboard_obj, created = BodegaDashboard.objects.get_or_create(bd_ID=bodega,bd_user=cliente)

        # Find BodegaOrders with their corresponding OrderItem
        try:
            BodegaOrders_list = get_list_or_404(BodegaOrders,bo_bodega=bodega)
        except:
            BodegaOrders_list = None

        OrderItem_list = []
        try:
            for bodega_order in BodegaOrders_list:
                item_list = get_list_or_404(OrderItem,oi_bo_ID=bodega_order,oi_is_anulado=False) # Take out the 'anulados'
                for item in item_list:
                    if item in OrderItem_list:
                        pass
                    else:
                        OrderItem_list.append(item)
        except:
            pass

        # Update BodegaDashboard values
        try:
            update_values_BodegaDashboard(BodegaDashboard_obj, BodegaOrders_list)
        except:
            pass

        # Find the most sold products
        try:
            most_sold_products = find_most_sold_products(OrderItem_list)
        except:
            most_sold_products = []

        try:
            top_list_size = 10
            if len(most_sold_products) > top_list_size:
                top10_products = list(most_sold_products)[0:len(most_sold_products)]
            else:
                top10_products = list(most_sold_products)[0:top_list_size]
        except:
            top10_products = []

        most_sold_products = list(most_sold_products)

        ################################# PAGE CONTENT END #################################
        ####################################################################################
        # Second check in the footer to render only if cl_is_bodega, and avoid None or any other value
        if cliente.cl_is_bodega:
            context = {
                        'STATIC_URL': STATIC_URL,
                        'BodegaDashboard_obj': BodegaDashboard_obj,
                        'OrderItem_list': OrderItem_list,
                        'cliente': cliente,
                        'bodega': bodega,
                        'most_sold_products': most_sold_products,
                        'top10_products': top10_products
                    }
            return render(request=request,template_name="main/d-index.html",context=context)
        else:
            return HttpResponseRedirect(reverse('main:homepage'))

    else:
        return HttpResponseRedirect(reverse('main:homepage'))

def productos(request):
    if request.user.is_authenticated:
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        # Render only if it's bodega
        # To avoid any rendering or calculation if it's not a bodega
        if cliente.cl_is_bodega == False:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page
        ####################################################################################
        ################################### PAGE CONTENT ###################################
        # Search for client's bodega and it's data
        bodega = Bodega.objects.all().filter(bd_ID=cliente.cl_default_bodega).first()
        BodegaDashboard_obj, created = BodegaDashboard.objects.get_or_create(bd_ID=bodega,bd_user=cliente)

        # Find ProductosEnBodega
        try:
            ProductosEnBodega_list = get_list_or_404(ProductosEnBodega,peb_bodega=bodega)
        except:
            ProductosEnBodega_list = None
        # Get all missing productos aprobados
        ProductosAprobados_all = ProductosAprobados.objects.all().filter(pa_status=True).all()
        ProductosAprobados_missing = []
        try:
            if ProductosEnBodega_list == None: # ProductosEnBodega_list is empty
                ProductosAprobados_missing = ProductosAprobados_all
            else:
                for producto_en_bodega in ProductosEnBodega_list: # delete all producto_en_bodega from ProductosAprobados_all
                    ProductosAprobados_all = ProductosAprobados_all.filter(~Q(pa_ID = producto_en_bodega.peb_product.pa_ID))
                ProductosAprobados_missing = list(ProductosAprobados_all)
        except:
            pass

        # If save_product_changes was posted, apply changes
        if request.method == "POST" and request.is_ajax():
            # Changes
            changes = request.POST.get('changes',False)
            if changes != False:
                changes = json.loads(changes)
                save_product_changes(changes,ProductosEnBodega_list)
            # Add product
            additions = request.POST.get('additions',False)
            if additions != False:
                additions = json.loads(additions)
                save_additions(additions,bodega,ProductosAprobados_all)



        

        ################################# PAGE CONTENT END #################################
        ####################################################################################
        # Second check in the footer to render only if cl_is_bodega, and avoid None or any other value
        if cliente.cl_is_bodega:
            context = {
                        'STATIC_URL': STATIC_URL,
                        'ProductosAprobados_missing': ProductosAprobados_missing,
                        'ProductosEnBodega_list': ProductosEnBodega_list,
                        'cliente': cliente,
                        'bodega': bodega,
                    }
            return render(request=request,template_name="main/d-productos.html",context=context)
        else:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page

    else:
        return HttpResponseRedirect(reverse('main:homepage'))

def mibodega(request):
    if request.user.is_authenticated:
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        # Render only if it's bodega
        # To avoid any rendering or calculation if it's not a bodega
        if cliente.cl_is_bodega == False:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page
        ####################################################################################
        ################################### PAGE CONTENT ###################################
        # Search for client's bodega and it's data
        bodega = Bodega.objects.all().filter(bd_ID=cliente.cl_default_bodega).first()

        # If save_product_changes was posted, apply changes
        if request.method == "POST" and request.is_ajax():
            # Retrieve changes
            cl_first_name = request.POST.get('cl_first_name',False)
            cl_last_name = request.POST.get('cl_last_name',False)
            #bd_is_active = request.POST.get('bd_is_active',False)
            bd_name = request.POST.get('bd_name',False)
            bd_ruc = request.POST.get('bd_ruc',False)
            bd_raz_soc = request.POST.get('bd_raz_soc',False)
            bd_email = request.POST.get('bd_email',False)
            bd_phone = request.POST.get('bd_phone',False)
            bd_delivery = request.POST.get('bd_delivery',False)
            bd_delivery_type = request.POST.get('bd_delivery_type',False)
            bd_delivery_cost = request.POST.get('bd_delivery_cost',False)
            bd_delivery_free_starting_on = request.POST.get('bd_delivery_free_starting_on',False)
            bd_delivery_conditions = request.POST.get('bd_delivery_conditions',False)
            bd_geolocation_lat = request.POST.get('bd_geolocation_lat',False)
            bd_geolocation_lng = request.POST.get('bd_geolocation_lng',False)
            #if bd_is_active == "true":
            #    bd_is_active = True
            #else:
            #    bd_is_active = False
            #bodega.bd_is_active = bd_is_active

            # Assign changes
            cliente.cl_first_name = cl_first_name
            cliente.cl_last_name = cl_last_name
            bodega.bd_name = bd_name
            bodega.bd_ruc = bd_ruc
            bodega.bd_raz_soc = bd_raz_soc
            bodega.bd_email = bd_email
            bodega.bd_phone = bd_phone
            if bd_delivery == "true":
                bd_delivery = True
            else:
                bd_delivery = False
            bodega.bd_delivery = bd_delivery
            if bd_delivery_type == "true":
                bd_delivery_type = True
            else:
                bd_delivery_type = False
            bodega.bd_delivery_type = bd_delivery_type
            bodega.bd_delivery_cost = float(bd_delivery_cost)
            bodega.bd_delivery_free_starting_on = float(bd_delivery_free_starting_on)
            bodega.bd_delivery_conditions = bd_delivery_conditions
            # Allow empty value for geolocation to be saved as in a newly created bodega/account
            try:
                user_location = Point(float(bd_geolocation_lng),float(bd_geolocation_lat),srid=4326)
            except:
                user_location = ""
            bodega.bd_geolocation = user_location
            
            # Save changes
            cliente.save()
            bodega.save()

            context = {
                'success': '',
            }

            return render(request=request,template_name="main/d-mibodega.html",context=context)

        ################################# PAGE CONTENT END #################################
        ####################################################################################
        # Second check in the footer to render only if cl_is_bodega, and avoid None or any other value
        if cliente.cl_is_bodega:
            context = {
                        'cliente': cliente,
                        'bodega': bodega,
                    }
            return render(request=request,template_name="main/d-mibodega.html",context=context)
        else:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page

    else:
        return HttpResponseRedirect(reverse('main:homepage'))

def pedidos(request):
    if request.user.is_authenticated:
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        # Render only if it's bodega
        # To avoid any rendering or calculation if it's not a bodega
        if cliente.cl_is_bodega == False:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page
        ####################################################################################
        ################################### PAGE CONTENT ###################################
        # Search for client's bodega and it's data
        bodega = Bodega.objects.all().filter(bd_ID=cliente.cl_default_bodega).first()

        

        ################################# PAGE CONTENT END #################################
        ####################################################################################
        # Second check in the footer to render only if cl_is_bodega, and avoid None or any other value
        if cliente.cl_is_bodega:
            context = {
                        'cliente': cliente,
                        'bodega': bodega,
                    }
            return render(request=request,template_name="main/d-pedidos.html",context=context)
        else:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page

    else:
        return HttpResponseRedirect(reverse('main:homepage'))

def tutorial(request):
    if request.user.is_authenticated:
        cliente = Cliente.objects.all().filter(cl_user=request.user).first()
        # Render only if it's bodega
        # To avoid any rendering or calculation if it's not a bodega
        if cliente.cl_is_bodega == False:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page
        ####################################################################################
        ################################### PAGE CONTENT ###################################
        # Search for client's bodega and it's data
        bodega = Bodega.objects.all().filter(bd_ID=cliente.cl_default_bodega).first()

        

        ################################# PAGE CONTENT END #################################
        ####################################################################################
        # Second check in the footer to render only if cl_is_bodega, and avoid None or any other value
        if cliente.cl_is_bodega:
            context = {
                        'cliente': cliente,
                        'bodega': bodega,
                    }
            return render(request=request,template_name="main/d-tutorial.html",context=context)
        else:
            return HttpResponseRedirect(reverse('main:homepage')) # pending to redirect to client page

    else:
        return HttpResponseRedirect(reverse('main:homepage'))

####################################################################################
################################# PYTHON FUNCTIONS #################################

def update_values_BodegaDashboard(BodegaDashboard_obj, BodegaOrders_list):
#        print("Today's week: ", date.today().isocalendar()[1]) # (ISO Year, ISO Week Number, ISO Weekday), always start on monday
#        print("order.bo_date_created: ", order.bo_date_created.strftime('%W')) # %W week starts on monday, %w starts on sunday

    today_sales = 0
    week_sales = 0
    month_sales = 0
    last_day_sales = 0
    last_week_sales = 0
    last_month_sales = 0
    for order in BodegaOrders_list:
        # Daily sales
        if str(order.bo_date_created.strftime('%Y-%m-%d')) == str(date.today()):
            today_sales += order.bo_total_price
        # Weekly sales
        if str(int(order.bo_date_created.strftime('%W'))+1) == str(date.today().isocalendar()[1]):
            week_sales += order.bo_total_price
        # Monthly sales
        if str(order.bo_date_created.strftime('%Y-%m')) == str( str(date.today().year)+"-"+"{:02d}".format(date.today().month)):
            month_sales += order.bo_total_price
        # Previos Daily sales
        if str(order.bo_date_created.strftime('%Y-%m-%d')) == str(date.today()+relativedelta(days=-1)):
            last_day_sales += order.bo_total_price
        # Previos Weekly sales
        if str(int(order.bo_date_created.strftime('%W'))+1) == str((date.today()+relativedelta(weeks=-1)).isocalendar()[1]):
            last_week_sales += order.bo_total_price
        # Previos Monthly sales
        if str(order.bo_date_created.strftime('%Y-%m')) == str( str(date.today().year)+"-"+"{:02d}".format((date.today()+relativedelta(months=-1)).month) ):
            last_month_sales += order.bo_total_price
    # Sale changes
    if last_day_sales != 0:
        daily_change_sales = (today_sales - last_day_sales)/last_day_sales*100
    else:
        daily_change_sales = 0
    if last_week_sales != 0:
        weekly_change_sales = (week_sales - last_week_sales)/last_week_sales*100
    else:
        weekly_change_sales = 0
    if last_month_sales != 0:
        monthly_change_sales = (month_sales - last_month_sales)/last_month_sales*100
    else:
        monthly_change_sales = 0

    # Save object
    BodegaDashboard_obj.bd_daily_sales = today_sales
    BodegaDashboard_obj.bd_weekly_sales = week_sales
    BodegaDashboard_obj.bd_monthly_sales = month_sales
    BodegaDashboard_obj.bd_last_day_sales = last_day_sales
    BodegaDashboard_obj.bd_last_week_sales = last_week_sales
    BodegaDashboard_obj.bd_last_month_sales = last_month_sales
    BodegaDashboard_obj.bd_daily_change_sales = daily_change_sales
    BodegaDashboard_obj.bd_weekly_change_sales = weekly_change_sales
    BodegaDashboard_obj.bd_monthly_change_sales = monthly_change_sales
    BodegaDashboard_obj.save()

def find_most_sold_products(OrderItem_list):
    most_sold_products = dict()
    for item in OrderItem_list:
        if item.oi_date_created.date() > (date.today()+timedelta(days = -30)):
            if item.oi_id_product in most_sold_products:
                # Tuple can not be updated, so convert it to list before updating a value
                temp = list(most_sold_products[str(item.oi_id_product)])
                temp[0] += int(item.oi_quantity)
                temp[2] += Decimal(item.oi_prod_total)
                most_sold_products[str(item.oi_id_product)] = tuple(temp)
            else:
                most_sold_products.update({
                    str(item.oi_id_product): ( int(item.oi_quantity), str(item.oi_product), Decimal(item.oi_prod_total) )
                })
    most_sold_products = sorted(most_sold_products.items(), key=lambda x: x[1][0], reverse=True)

    # In case adding enumeration is needed
#    ranked_most_sold_products = enumerate(list(most_sold_products)[0:list_size],start=1)
#    print(most_sold_products[1][:])
    return most_sold_products

def save_product_changes(changes, ProductosEnBodega_list):
    for product_changes in changes:
        for producto in ProductosEnBodega_list:
            if str(producto.peb_ID) == str(product_changes['key']):
                producto.peb_regular_price = product_changes['regular_price']
                producto.peb_discount_price = product_changes['discount_price']
                producto.peb_discount_status = product_changes['discount_status']
                producto.peb_status = product_changes['peb_status']
                producto.peb_discount_rate = product_changes['n_discount_rate']
                producto.save()
                break
    #return redirect('main:productos')
    return JsonResponse({"success": ""}, status=200)

def save_additions(additions, bodega, ProductosAprobados_all):
    for product_to_add in additions:
        producto_aprobado = ProductosAprobados_all.filter(pa_ID=str(product_to_add['key'])).first()
        if producto_aprobado.pa_suggested_price > 0: # if the suggested price is valid, enables the product
            new_item_obj, created = ProductosEnBodega.objects.get_or_create(peb_bodega=bodega,peb_product=producto_aprobado,peb_regular_price=producto_aprobado.pa_suggested_price,peb_status=True)
        else: # otherwise product starts as disabled
            new_item_obj, created = ProductosEnBodega.objects.get_or_create(peb_bodega=bodega,peb_product=producto_aprobado,peb_status=False)
    #return redirect('main:productos')
    return JsonResponse({"success": ""}, status=200)

def remove_product(request):
    if request.method == "POST" and request.is_ajax():
        remove_product_id = request.POST.get('key',False)
        if remove_product_id != False:
            rm_obj = get_object_or_404(ProductosEnBodega,peb_ID=remove_product_id)
            rm_obj.delete()
            return JsonResponse({"success": ""}, status=200)
        else:
            return JsonResponse({"error": "no product to delete"}, status=400)

def see_sales_detail(request):
    if request.method == "POST" and request.is_ajax():
        product_id = request.POST.get('product_id',False)
        bodega_id = request.POST.get('bodega_id',False)
        if product_id != False and bodega_id != False:            
            # Retrieve bodega
            bodega = get_object_or_404(Bodega,bd_ID=bodega_id)
            try:
                BodegaOrders_list = get_list_or_404(BodegaOrders,bo_bodega=bodega)
            except:
                BodegaOrders_list = []

            OrderItem_list = []
            for bodega_order in BodegaOrders_list:
                try:
                    item = get_object_or_404(OrderItem,oi_bo_ID=bodega_order,oi_is_anulado=False,oi_id_product=str(product_id))
                    OrderItem_list.append(item)
                except:
                    pass

            products_details = dict()
            for item in OrderItem_list:
                if item.oi_date_created.date() > (date.today()+timedelta(days = -30)):
                    if item.oi_price in products_details:
                        products_details[str(item.oi_price)] += int(item.oi_quantity)
                    else:
                        products_details.update({
                            str(item.oi_price): int(item.oi_quantity)
                        })
            products_details = sorted(products_details.items(), key=lambda x: x[0], reverse=True)
            json_products_details = json.dumps(products_details)
            return JsonResponse({"success": json_products_details}, status=200)
        else:
            return JsonResponse({"error": "no product detail"}, status=400)

def unete(request):
    return render(request=request, # to reference request
                  template_name="main/unete.html", # where to find the specifix template
                  )

def get_nearby_shops(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieves user location
        user_latitude = request.POST.get('latitude',False)
        user_longitude = request.POST.get('longitude',False)
        # Find nearby shops
        user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
        shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=30000).order_by("distance")[0:10] # <------------ This distance to plot on map should be evaluated
        json_response = []
        for shop in shops:
            json_response.append( (shop.bd_geolocation.y, shop.bd_geolocation.x, shop.bd_name, shop.bd_ID) )
        return JsonResponse({"success": tuple(json_response)}, status=200)
    else:
        return JsonResponse({"error": "unknown"}, status=400)

def update_user_location(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieves user location
        user_latitude = request.POST.get('latitude',False)
        user_longitude = request.POST.get('longitude',False)
        # Stores in cache user location
        request.session['user_longitude'] = user_longitude
        request.session['user_latitude'] = user_latitude
        return JsonResponse({"success": ""}, status=200)
    else:
        return JsonResponse({"error": ""}, status=400)

def search_query(request):
    if request.method == "POST" and request.is_ajax():
        # Locate user and shops nearby.
        try:
            user_longitude = request.session['user_longitude']
            user_latitude = request.session['user_latitude']
            introduction = False
            user_location = Point(float(user_longitude),float(user_latitude),srid=4326)
        except:
            # Add guidance if it is the first time in the site
            request.session['introduction'] = True
            introduction = True
            # Using IpregistryClient to get user aprox location or user_longitude = 0 user_latitude = 0
            user_longitude = -76.944204
            user_latitude = -12.109987
            #user_longitude, user_latitude = locate_user()
            user_location = Point(float(user_longitude),float(user_latitude),srid=4326)

        # Retrieves search_text        
        search_text = request.POST.get('search_text',False)
        # Get search words
        search_words = search_text.split(" ")
        # Remove empty entries
        while('' in search_words):
            search_words.remove('')

        # Find shops nearby the user
        shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).filter(distance__lt=1500).order_by("distance")[0:10]
        
        # Retrieve all products from nearby shops
        productos_en_bodegas = ProductosEnBodega.objects.all()
        result_list = []
        for shop in shops:
            temp = productos_en_bodegas.filter(peb_product__pa_status=True,peb_bodega=shop,peb_bodega__bd_is_active=True,peb_status=True,peb_regular_price__gt=0)
            for product in temp:
                product_already_in_result_list = False
                for item in result_list:
                    if item.peb_product.pa_ID == product.peb_product.pa_ID:
                        product_already_in_result_list = True
                        if item.peb_discount_price > product.peb_discount_price:
                            result_list.remove(item) # Removes existing more expensive item
                            result_list.append(product) # Adds new cheaper product
                        else:
                            break
                if product_already_in_result_list == False:
                    result_list.append(product) # Add new product to the list
                else:
                    product_already_in_result_list = False
        shuffle(result_list)
        
        # Search for the best results
        result_dict = dict()
        for product in result_list:
            search_score = 0
            for i in range(0,len(search_words)):
                # Normalize string (eliminates accents)
                string_producto = str(product.peb_product.pa_product)
                string_producto = unidecode.unidecode(string_producto)
                search_w = search_words[i]
                search_w = unidecode.unidecode(search_w)
                # Look for matching word
                # usr_geolocation with regex
                patterns = '^(.*?(' + search_w + ')[^$]*)$'
                match = re.findall(patterns, string_producto, re.IGNORECASE) # Full match 0 is SRID, Full match 1 is Lng, Full match 2 is Lat
                search_score += len(match)

            if (search_score != 0):
                if product.peb_discount_status == True and product.peb_discount_price > 0: # If is in discount and has a valid discount price
                    result_dict.update({
                        str(product.peb_ID) : (str(product.peb_product.pa_product), str(product.peb_product.pa_image.url), str(product.peb_discount_price), search_score)
                    })
                elif product.peb_discount_status == False: # If is not in discount (but has a valid regular price)
                    result_dict.update({
                        str(product.peb_ID) : (str(product.peb_product.pa_product), str(product.peb_product.pa_image.url), str(product.peb_regular_price), search_score)
                    })
                else: # If has an invalid discount price (0 or less than 0)
                    pass
        
        # Sort items according to most suitable case
        def comparator_price( tupleElem ):
            #print("tupleElem[1][3]: ", tupleElem[1][3])
            return tupleElem[1][3]
        result_dict = sorted(result_dict.items(), key=comparator_price, reverse=True)
        return JsonResponse({"success": json.dumps(result_dict[0:4])}, status=200)

def search_username(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieves username
        username = request.POST.get('username',False)
        if username != False:
            try:
                user= User.objects.get(username=username)
                return JsonResponse({"error": "Este usuario ya está en uso. Por favor, escriba otro."}, status=400)
            except User.DoesNotExist:
                return JsonResponse({"success": "Este usuario disponible"}, status=200)
        else:
            return JsonResponse({"error": "error desconocido"}, status=400)
    else:
        return redirect('main:homepage')

def search_ruc(request):
    if request.method == "POST" and request.is_ajax():
        # Retrieves ruc or dni
        ruc = request.POST.get('ruc',False)
        if ruc != False:
            try:
                ruc= Bodega.objects.get(bd_ruc=ruc)
                return JsonResponse({"error": "Este ruc ya está registrado."}, status=400)
            except Bodega.DoesNotExist:
                return JsonResponse({"success": "Este ruc aún no está registrado"}, status=200)
        else:
            return JsonResponse({"error": "error desconocido"}, status=400)
    else:
        return redirect('main:homepage')