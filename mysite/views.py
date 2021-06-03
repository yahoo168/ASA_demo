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
from restaurants.models import StockPrice

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
    print(request.POST)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect('/accounts/login/')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', locals())

def index(request):
    stockPrice_df = pd.DataFrame(list(StockPrice.objects.all().values()))
    #以資料庫最新的價格在首頁展示（FB、MSFT）
    fb_latest_price = round((stockPrice_df["fb"]).iloc[-1], 2)
    msft_latest_price = round((stockPrice_df["msft"]).iloc[-1], 2)
    tsla_latest_price = round((stockPrice_df["tsla"]).iloc[-1], 2)
    latest_date = (stockPrice_df["date"]).iloc[-1]
    latest_date = latest_date.strftime("%Y-%m-%d")
    # 五個plot放重要的幾個股票指數
    # result_df = stock_DB['AAPL']
    result_df = pd.DataFrame()
    # time = np.array(0,len(result_df))
    # #draw plot
    # from matplotlib.font_manager import FontProperties
    # fig, ax = plt.subplots()
    # ax.plot(time, result_df)
    # ax.set(xlabel='time (s)', ylabel='price',
    #        title='APPL stock price')
    # ax.grid()

    # #return
    # response = HttpResponse(content_type = 'image/png')
    # canvas = FigureCanvasAgg(fig)
    # canvas.print_png(response)
    return render(request, 'index.html', locals())

def keyword_search(request): #搜尋關鍵字
    post_dict = request.POST

    # TODO: report_DB要改掉
    if post_dict['reporter'] == True:
        data = report_DB[report_DB["username"] == post_dict['content']]
    elif post_dict['stock'] == True:
        data = post_dict[post_dict["stockname"] == post_dict['content']]
    elif post_dict['date'] == True:
        data = post_dict[post_dict["date"] == post_dict['content']]

    json_df = data.to_json(orient ='records')
    data = json.loads(json_df)
    return render(request, 'index.html', locals())

def evaluation_period(request):
    post_dict = request.POST

    #TODO: 改DB
    data = report_DB[report_DB["index"] == post_dict['report_index']]
    price1 = data['price1']
    price2 = data['price2']
    price3 = data['price3']

    prob1 = data['prediction1']
    prob2 = data['prediction1']
    prob3 = data['prediction1']

    #TODO: 改DB
    error = {(price1 - stock_DB[post_dict['stockname']]['''第一期的price''']) * prob1 +
             (price2 - stock_DB[post_dict['stockname']]['''第二期的price''']) * prob2 +
             (price3 - stock_DB[post_dict['stockname']]['''第三期的price''']) * prob3 }

    target_change = price1 * prob1 + price2 * prob2 + price3 * prob3

    error_score = error / target_change
    return render(request, 'index.html', error_score)

def add_report(request):
    post_dict = request.POST

    #TODO: 給新的reort一個自己的id
    index = "Report001"

    reporter = post_dict["reporter"]
    stockname = post_dict["stock"]
    date = post_dict["date"]
    price1 = post_dict["price1"]
    predProb1 = post_dict["prediction1"]
    price2 = post_dict["price2"]
    predProb2 = post_dict["prediction2"]
    price3 = post_dict["price3"]
    predProb3 = post_dict["prediction3"]
    content = post_dict["content"]

    #TODO (Report要寫一個model.py來做一個class)
    Report.objects.create(index = index, reporter = reporter, stockname = stockname, date = date, price1 = price1, predProb1 = predProb1, price2 = price2, predProb2 = predProb2, price3 = price3, predProb3 = predProb3, content = content)
    alert_message = "已成功新增報告"
    return render(request, 'index.html', locals())


def delete_report(request):
    post_dict = request.POST

    reporter = post_dict["reporter"]
    stockname = post_dict["stock"]
    date = post_dict["date"]
    price1 = post_dict["price1"]
    predProb1 = post_dict["prediction1"]
    price2 = post_dict["price2"]
    predProb2 = post_dict["prediction2"]
    price3 = post_dict["price3"]
    predProb3 = post_dict["prediction3"]
    content = post_dict["content"]

    #TODO (Report要寫一個model.py來做一個class)
    report = Report.objects.get(reporter = reporter, stockname = stockname, date = date, price1 = price1, predProb1 = predProb1, price2 = price2, predProb2 = predProb2, price3 = price3, predProb3 = predProb3, content = content)
    report.delete()
    alert_message = "已成功刪除報告"
    return render(request, 'index.html', locals())
