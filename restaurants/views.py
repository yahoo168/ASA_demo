from django.http import HttpResponse
from django.shortcuts import render

def here(request):
    return HttpResponse('Mom, I am here!')

def add(request, a, b): # <- 加入這個函式
    s = int(a) + int(b)
    a = {"s":s}
    return render(request, 'menu.html', locals())