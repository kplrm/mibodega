from django.shortcuts import render

def dashboard(request):
    return render(request=request, # to reference request
                  template_name="dashboard/index.html", # where to find the specifix template
                  context={})