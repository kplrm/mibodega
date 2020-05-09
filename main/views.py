from django.shortcuts import render, redirect, get_object_or_404 # to redirect the user
from .models import ProductosEnBodega, Cart, CartItem, Cliente, Bodega
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

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from ipregistry import IpregistryClient, NoCache

import json

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
    print("Entering remove_cart")
    print(request.POST)
    item_pk = request.POST.get('item_pk', None)
    print("item_pk")
    print(item_pk)
    item_obj = CartItem.objects.all().filter(pk=item_pk).first()
    print("item_obj")
    print(item_obj)
    cart_obj = Cart.objects.all().filter(crt_ID=item_obj.ci_cart_ID).first()
    print("cart_obj")
    print(cart_obj)

    cart_obj.crt_product.remove(item_obj.ci_product)
    print(cart_obj)
    cart_obj.crt_item.remove(item_obj)
    print(cart_obj)
    item_obj.delete()

    update_price(cart_obj)
    #return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
    #return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponse("")

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
