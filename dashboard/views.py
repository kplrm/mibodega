from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from main.models import Cliente, Bodega
from .models import BodegaDashboard

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
        obj, created = BodegaDashboard.objects.get_or_create(bd_ID=bodega,bd_user=cliente)
        print("created? ", created)

        update_values_BodegaDashboard()













        ################################# PAGE CONTENT END #################################
        ####################################################################################
        # Second check in the footer to render only if cl_is_bodega, and avoid None or any other value
        if cliente.cl_is_bodega:
            return render(request=request,
                  template_name="dashboard/index.html")
        else:
            return HttpResponseRedirect(reverse('main:homepage'))

    else:
        return HttpResponseRedirect(reverse('main:homepage'))

def update_values_BodegaDashboard():
    pass