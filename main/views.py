from django.shortcuts import render, redirect, get_object_or_404 # to redirect the user
from .models import ProductosEnBodega, Cart, Cliente
from django.urls import reverse

from .forms import RegistrationForm, ClientForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages # to send unique messages to the users

from itertools import chain

# Create your views here.
def homepage(request):
    # Load current offers
    productos_en_bodegas = ProductosEnBodega.objects.all()
    result_list = productos_en_bodegas.filter(peb_discount_rate__lt=0).order_by('peb_discount_rate')[:10]

    # Load or create cart
    cart_obj = session_cart_load_or_create(request)
    #print(cart_obj)
    #add_to_cart = CartForm(request.POST)

    return render(request=request, # to reference request
                  template_name="main/index.html", # where to find the specifix template
                  context={'result_list': result_list})

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

def cart_add(request):
    print("Entrando en el update!")
    product_obj = ProductosEnBodega.objects.all().filter(peb_ID=request.POST.get('product_id', None)).first()
    cart_obj, new_obj =  Cart.objects.new_or_get(request)
    if product_obj in cart_obj.crt_product.all():
        cart_obj.crt_product.remove(product_obj)
    else:
        cart_obj.crt_product.add(product_obj)
    return redirect('main:homepage')

    # identifies the product where the mouse was clicked on
    #item = get_object_or_404(ProductosEnBodega,peb_slug=slug)
    # find the client
    #cliente = get_object_or_404(Cliente,cl_user=request.user)
    # searches if this product exists already in the basket
    #basket_item,created = Basket.objects.get_or_create(bkt_product=item,bkt_user=cliente,bkt_ordered=False)
    # To make sure not to pass an already completed  order.
    #order_qs = Order.objects.filter(user=request.user,ordered=False)
    #if order_qs.exists():
    #    order = order_qs[0]
        # check if the basket_item is in the order
    #    if order.items.filter(item__slug=item.slug).exists():
    #        basket_item.bkt_quantity += 1
    #        basket_item.save()
    #    else:
    #        order.item.add(basket_item)
    #else:
    #    order = Order.objects.create(user=request.user,ordered_date=timezone.now())
    #    order.items.add(basket_item)
    #return redirect("main/index.html")