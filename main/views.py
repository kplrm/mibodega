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
from django.http import HttpResponseRedirect

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from ipregistry import IpregistryClient, NoCache

# Global variable Loads MEDIA_URL
MEDIA_URL = settings.MEDIA_URL

def locate_user():
    client = IpregistryClient("2cc3d6z6ct2weq", cache=NoCache())
    ipInfo = client.lookup()
    user_longitude = ipInfo.location['longitude']
    user_latitude = ipInfo.location['latitude']
    return user_longitude, user_latitude

def select_shop(request):
    longitude, latitude = locate_user()
    user_location = Point(longitude,latitude,srid=4326)
    print("User location")
    print(longitude)
    print(latitude)

    shops = Bodega.objects.annotate(distance=Distance("bd_geolocation",user_location)).order_by("distance")[0:6]
    return render(request=request,
                  template_name="main/select_shop.html",
                  context={'user_location': user_location, 'shops': shops})

def homepage(request):
#    user_latitude, user_longitude = locate_user()
    # Load current offers
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0)[:20]
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
                  context={'result_list': result_list,'cart_obj': cart_obj,'cart_list': cart_list, 'MEDIA_URL': MEDIA_URL})

def embutidos(request):
    # Load embutidos
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="embutidos").all()
    result_list = productos_en_bodegas
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
            print(product.peb_product.pa_brand)
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
                  'MEDIA_URL': MEDIA_URL})

def lacteos(request):
    # Load lacteos
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="lacteos").all()
    result_list = productos_en_bodegas
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
            print(product.peb_product.pa_brand)
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
                  'MEDIA_URL': MEDIA_URL})

def abarrotes(request):
    # Load abarrotes
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="abarrotes").all()
    result_list = productos_en_bodegas
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
            print(product.peb_product.pa_brand)
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
                  'MEDIA_URL': MEDIA_URL})

def limpieza(request):
    # Load limpieza
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="limpieza").all()
    result_list = productos_en_bodegas
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
            print(product.peb_product.pa_brand)
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
                  'MEDIA_URL': MEDIA_URL})

def licores(request):
    # Load licores
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="licores").all()
    result_list = productos_en_bodegas
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
            print(product.peb_product.pa_brand)
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
                  'MEDIA_URL': MEDIA_URL})

def vegetales(request):
    # Load vegetales
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="vegetales").all()
    result_list = productos_en_bodegas
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
            print(product.peb_product.pa_brand)
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
                  'MEDIA_URL': MEDIA_URL})

def checkout(request):
    # Load vegetales
    productos_en_bodegas = ProductosEnBodega.objects.all().filter(peb_product__pa_category="vegetales").all()
    result_list = productos_en_bodegas
    
    # Load or create cart
    cart_obj, new_obj = session_cart_load_or_create(request)
    # Load item list
    cart_list = CartItem.objects.all().filter(ci_cart_ID=cart_obj.crt_ID).all()

    return render(request=request, # to reference request
                  template_name="main/checkout.html", # where to find the specifix template
                  context={'result_list': result_list,
                  'cart_obj': cart_obj,
                  'cart_list': cart_list,
                  'MEDIA_URL': MEDIA_URL})

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
    print("yeeeee")
    item_pk = request.POST.get('item_pk', None)
    item_obj = CartItem.objects.all().filter(pk=item_pk).first()
    cart_obj = Cart.objects.all().filter(crt_ID=item_obj.ci_cart_ID).first()

    cart_obj.crt_product.remove(item_obj.ci_product)
    cart_obj.crt_item.remove(item_obj)
    item_obj.delete()

    update_price(cart_obj)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

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
