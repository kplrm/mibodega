from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from main.models import Cliente, Bodega, OrderItem, BodegaOrders
from .models import BodegaDashboard

from datetime import date
from dateutil.relativedelta import relativedelta

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
            item_list = get_list_or_404(OrderItem,oi_bo_ID=bodega_order,oi_is_anulado=False) # Take out the 'anulados'
            for item in item_list:
                if item in OrderItem_list:
                    pass
                else:
                    OrderItem_list.append(item)
        print("BodegaOrders_list? ", len(BodegaOrders_list))
        print("OrderItem_list? ", len(OrderItem_list))

        # Update BodegaDashboard values
        update_values_BodegaDashboard(BodegaDashboard_obj, BodegaOrders_list, OrderItem_list)




        ################################# PAGE CONTENT END #################################
        ####################################################################################
        # Second check in the footer to render only if cl_is_bodega, and avoid None or any other value
        if cliente.cl_is_bodega:
            context = {
                        'BodegaDashboard_obj': BodegaDashboard_obj
                    }
            return render(request=request,template_name="dashboard/index.html",context=context)
        else:
            return HttpResponseRedirect(reverse('main:homepage'))

    else:
        return HttpResponseRedirect(reverse('main:homepage'))

####################################################################################
################################# PYTHON FUNCTIONS #################################

def update_values_BodegaDashboard(BodegaDashboard_obj, BodegaOrders_list, OrderItem_list):
#        print("Today's week: ", date.today().isocalendar()[1]) # (ISO Year, ISO Week Number, ISO Weekday), always start on monday
#        print("order.bo_date_created: ", order.bo_date_created.strftime('%W')) # %W week starts on monday, %w starts on sunday

    today_sales = 0
    week_sales = 0
    month_sales = 0
    last_day_sales = 0
    last_week_sales = 0
    last_month_sales = 0
    print("Yesterday: ", date.today()+relativedelta(days=-1))
    print("Last month: ", date.today()+relativedelta(months=-1))
    for order in BodegaOrders_list:
        # Daily sales
        if str(order.bo_date_created.strftime('%Y-%m-%d')) == str(date.today()):
            today_sales += order.bo_total_price
        # Weekly sales
        if str(int(order.bo_date_created.strftime('%W'))+1) == str(date.today().isocalendar()[1]):
            week_sales += order.bo_total_price
        # Monthly sales
        if str(order.bo_date_created.strftime('%Y-%m')) == str(str(date.today().year)+"-"+str(date.today().month)):
            month_sales += order.bo_total_price
        # Previos Daily sales
        if str(order.bo_date_created.strftime('%Y-%m-%d')) == str(date.today()+relativedelta(days=-1)):
            last_day_sales += order.bo_total_price
        # Previos Weekly sales
        if str(int(order.bo_date_created.strftime('%W'))) == str(date.today().isocalendar()[1]):
            last_week_sales += order.bo_total_price
        # Previos Monthly sales
#        if str(order.bo_date_created.strftime('%Y-%m')) == str(str(date.today().year)+"-"+str(date.today().month)):
#            last_month_sales += order.bo_total_price

    BodegaDashboard_obj.bd_daily_sales = today_sales
    BodegaDashboard_obj.bd_weekly_sales = week_sales
    BodegaDashboard_obj.bd_monthly_sales = month_sales
    BodegaDashboard_obj.bd_last_day_sales = last_day_sales
    BodegaDashboard_obj.bd_last_week_sales = last_week_sales
    BodegaDashboard_obj.bd_last_month_sales = last_month_sales

    BodegaDashboard_obj.save()

