from django.shortcuts import render, redirect # to redirect the user
from .models import ProductosEnBodega

from .forms import RegistrationForm, ClientForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages # to send unique messages to the users

from itertools import chain

# Create your views here.
def homepage(request):
    #DG
    # Entry tiene el foreign key de Blog como blog
    productos_en_bodegas = ProductosEnBodega.objects.all()
    productos_en_oferta = productos_en_bodegas.filter(peb_discount_rate__lt=0)
#    print(productos_en_oferta)
#    filtro_ofertas_ld = lista_de_productos.filter(ld_discount_rate__lt=0)
#    filtro_ofertas_pa = ProductosAprobados.objects.filter(pk__in=filtro_ofertas_ld.values('ld_product'))

    # Order by pk
#    filtro_ofertas_pa = filtro_ofertas_pa.order_by('pk')
#    filtro_ofertas_ld = filtro_ofertas_ld.order_by('ld_product')

    # Join querysets in a list of dictionaries
    result_list = []
#    for product in filtro_ofertas_pa:
#        result_list.append({'pa_photo_small':product.pa_photo_small,
#                    'pa_category':product.pa_category,
#                    'pa_product':product.pa_product,
#                    'ld_regular_price':"",
#                    'ld_discount_price':"",
#                    'ld_discount_rate':"",
#                    })
#    counter = 0
#    for product in filtro_ofertas_ld:
#        result_list[counter]['ld_regular_price'] = str(format(product.ld_regular_price,'.2f'))
#        result_list[counter]['ld_discount_price'] = str(format(product.ld_discount_price,'.2f'))
#        result_list[counter]['ld_discount_rate'] = int(round(product.ld_discount_rate))
#        counter = counter+1

    return render(request=request, # to reference request
                  template_name="main/index.html", # where to find the specifix template
                  context={'result_list': result_list})

def register(request):
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