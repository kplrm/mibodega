from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from main.models import Cliente, Bodega, OrderItem, BodegaOrders
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
        BodegaDashboard_obj, created = BodegaDashboard.objects.get_or_create(bd_ID=bodega,bd_user=cliente)
        print("created? ", created)

        # Find BodegaOrders with their corresponding OrderItem
        BodegaOrders_list = get_list_or_404(BodegaOrders,bo_bodega=bodega)
        OrderItem_list = []
        for bodega_order in BodegaOrders_list:
            item_list = get_list_or_404(OrderItem,oi_bo_ID=bodega_order,oi_is_anulado=False)
            for item in item_list:
                if item in OrderItem_list:
                    pass
                else:
                    OrderItem_list.append(item)
        print("BodegaOrders_list? ", len(BodegaOrders_list))
        print("OrderItem_list? ", len(OrderItem_list))



        update_values_BodegaDashboard(BodegaOrders_list)













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

####################################################################################
################################# PAGE A #################################

def update_values_BodegaDashboard(BodegaOrders_list):
    pass