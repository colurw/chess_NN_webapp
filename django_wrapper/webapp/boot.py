""" Receives requests from browser for /index. Returns index.html before delay 
    caused by models loading into memory when views.py is first run """

from django.shortcuts import render

def index(request):
    return render(request, "index.html")