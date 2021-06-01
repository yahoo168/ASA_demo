from django.contrib import auth
from django import forms
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/index/')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    print("username",username, password)
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponseRedirect('/index/')
    else:
        return render(request, 'log_in.html', locals())

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/accounts/login/')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect('/accounts/login/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', locals())

def index(request):
    return render(request, 'index.html')

def keyword_search(request): #搜尋關鍵字
#接收前端的 request -> ex: 姓名搜尋
    post_dict = request.POST
    if request.type == "name":
        result_df = post_dict[post_dict["username"] == request.username]
    elif request.type == "stock":
        result_df = post_dict[post_dict["stockname"] == request.stockname]

    json_df = result_df.to_json(orient ='records')
    data = json.loads(json_df)
    context = {'d':data}
    # 須確認頁面
    return render(request, 'index.html', context)

#def plot_evaluation_period(request):

def show_homepage_index(request):
# 五個plot放重要的幾個股票指數
    stock_dict = request.POST.stockPrice #??
    result_df = stock_dict['AAPL']
    time = np.array(0,len(result_df),1)
    #draw plot
    from matplotlib.font_manager import FontProperties
    fig, ax = plt.subplots()
    ax.plot(time, result_df)
    ax.set(xlabel='time (s)', ylabel='price',
           title='APPL stock price')
    ax.grid()

    #return
    response = HttpResponse(content_type = 'image/png')
    canvas = FigureCanvasAgg(fig)
    canvas.print_png(response)
    return render(request, 'index.html', response)

def add_report(request):
    post_dict = request.POST

    username = post_dict["username"]
    stockname = post_dict["stockname"]
    date = post_dict["date"]
    expPrice = post_dict["expPrice"]
    predProb = post_dict["predProb"]

    Report.objects.create(username = username, stockname = stockname, date = date, expPrice = expPrice, predProb = predProb)
    alert_message = "已成功新增報告"
    return render(request, 'add_data.html', locals())


def delete_report(request):
    post_dict = request.POST

    username = post_dict["username"]
    stockname = post_dict["stockname"]
    date = post_dict["date"]
    expPrice = post_dict["expPrice"]
    predProb = post_dict["predProb"]

    report = Report.objects.get(username = username, stockname = stockname, date = date, expPrice = expPrice, predProb = predProb)
    report.delete()
    alert_message = "已成功刪除報告"
    return render(request, 'index.html', locals())