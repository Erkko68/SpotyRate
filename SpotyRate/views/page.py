from django.shortcuts import render

def landing(request):
    return render(request, "landing.html")

def dashboard(request):
    # This will render the default dashboard page with the search bar included
    return render(request, 'dashboard.html')