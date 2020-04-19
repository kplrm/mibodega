from django.shortcuts import render, redirect # to redirect the user
from .models import ProductosAprobados, ListaDeProductos

from .forms import RegistrationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages # to send unique messages to the users

from itertools import chain

# Create your views here.
def homepage(request):
    #DG
    # Entry tiene el foreign key de Blog como blog
    lista_de_productos = ListaDeProductos.objects.all()
    filtro_ofertas_ldp = lista_de_productos.filter(ldp_discount_rate__lt=0)
    filtro_ofertas_pa = ProductosAprobados.objects.filter(pk__in=filtro_ofertas_ldp.values('ldp_product'))

    # Order by pk
    filtro_ofertas_pa = filtro_ofertas_pa.order_by('pk')
    filtro_ofertas_ldp = filtro_ofertas_ldp.order_by('ldp_product')

    # Join querysets in a list of dictionaries
    result_list = []
    for product in filtro_ofertas_pa:
        result_list.append({'pa_photo_small':product.pa_photo_small,
                    'pa_category':product.pa_category,
                    'pa_product':product.pa_product,
                    'ldp_regular_price':"",
                    'ldp_discount_price':"",
                    'ldp_discount_rate':"",
                    })
    counter = 0
    for product in filtro_ofertas_ldp:
        result_list[counter]['ldp_regular_price'] = str(format(product.ldp_regular_price,'.2f'))
        result_list[counter]['ldp_discount_price'] = str(format(product.ldp_discount_price,'.2f'))
        result_list[counter]['ldp_discount_rate'] = int(round(product.ldp_discount_rate))
        counter = counter+1

    

    return render(request=request, # to reference request
                  template_name="main/index.html", # where to find the specifix template
                  context={'result_list': result_list})

def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
    return render(request, 'main/register.html', context={"form":form})

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
                print("exito")
                auth_login(request, user)
                messages.info(request,f"Bienvenido: {username}")
                return redirect('main:homepage')
            else:
                messages.error(request,f"Usuario o contraseña incorrecta")
        # in case the form is invalid
        messages.error(request,f"Usuario o contraseña incorrecta")

    form = AuthenticationForm()
    return render(request, "main/login.html", {"form":form})