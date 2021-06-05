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
import json
from restaurants.models import StockPrice, Report

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
    latest_date = (stockPrice_df["date"]).iloc[-1].strftime("%Y-%m-%d")

    report_df = pd.DataFrame(list(Report.objects.all().values()))
    report_df["original_price"] = report_df.apply(lambda x: round(stockPrice_df[x["stockname"].lower()], 2)[stockPrice_df.date <= x.date].iloc[-1], axis=1)
    report_df["latest_price"] = report_df.apply(lambda x: round(stockPrice_df[x["stockname"].lower()], 2).iloc[-1], axis=1)
    report_df["date"] = report_df.apply(lambda x: x.date.strftime("%Y-%m-%d"), axis=1)
    report_df["total_change"] = 100*round((report_df["latest_price"] - report_df["original_price"]) / report_df["original_price"], 2)
    report_df["target_price"] = report_df.apply(lambda x: cal_target_price(x.stockname, x.date, x.original_price, x.latest_price, x.price1, x.price2, x.price3, x.probability1, x.probability2, x.probability3), axis=1)
    report_df["score"] = report_df.apply(lambda x: evaluation_period(x.stockname, x.date, x.original_price, x.latest_price, x.price1, x.price2, x.price3, x.probability1, x.probability2, x.probability3), axis=1)
    
    report_df["probability1"] = 100 * report_df["probability1"]
    report_df["probability2"] = 100 * report_df["probability2"]
    report_df["probability3"] = 100 * report_df["probability3"]
    report_df.sort_values(by=['date'], inplace=True, ascending=False)
    json_df = report_df.to_json(orient='records')
    data = json.loads(json_df)

    
    # 五個plot放重要的幾個股票指數
    # result_df = stock_DB['AAPL']
    # result_df = pd.DataFrame()
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

def keyword_search(request):
    post_dict = request.POST
    stockPrice_df = pd.DataFrame(list(StockPrice.objects.all().values()))
    #以資料庫最新的價格在首頁展示（FB、MSFT）
    fb_latest_price = round((stockPrice_df["fb"]).iloc[-1], 2)
    msft_latest_price = round((stockPrice_df["msft"]).iloc[-1], 2)
    tsla_latest_price = round((stockPrice_df["tsla"]).iloc[-1], 2)
    latest_date = (stockPrice_df["date"]).iloc[-1].strftime("%Y-%m-%d")

    report_df = pd.DataFrame(list(Report.objects.all().values()))
    report_df["original_price"] = report_df.apply(lambda x: round(stockPrice_df[x["stockname"].lower()], 2)[stockPrice_df.date <= x.date].iloc[-1], axis=1)
    report_df["latest_price"] = report_df.apply(lambda x: round(stockPrice_df[x["stockname"].lower()], 2).iloc[-1], axis=1)
    report_df["date"] = report_df.apply(lambda x: x.date.strftime("%Y-%m-%d"), axis=1)
    report_df["total_change"] = 100*round((report_df["latest_price"] - report_df["original_price"]) / report_df["original_price"], 2)
    report_df["target_price"] = report_df.apply(lambda x: cal_target_price(x.stockname, x.date, x.original_price, x.latest_price, x.price1, x.price2, x.price3, x.probability1, x.probability2, x.probability3), axis=1)
    report_df["score"] = report_df.apply(lambda x: evaluation_period(x.stockname, x.date, x.original_price, x.latest_price, x.price1, x.price2, x.price3, x.probability1, x.probability2, x.probability3), axis=1)
    
    report_df["probability1"] = 100 * report_df["probability1"]
    report_df["probability2"] = 100 * report_df["probability2"]
    report_df["probability3"] = 100 * report_df["probability3"]
    report_df.sort_values(by=['date'], inplace=True, ascending=False)
    
    if 'reporter' in post_dict:
        data = report_df[report_df["name"] == post_dict['search']]
    elif 'stock_name' in post_dict:
        data = report_df[report_df["stockname"] == post_dict['search']]
    # elif 'date' in post_dict:
    #     data = report_df[report_df["date"] == post_dict['search']]
    
    json_df = data.to_json(orient='records')
    data = json.loads(json_df)
    return render(request, 'index.html', locals())

def cal_target_price(stockname, date, original_price, latest_price, price1, price2, price3, prob1, prob2, prob3):
    return price1 * prob1 + price2 * prob2 + price3 * prob3

def evaluation_period(stockname, date, original_price, latest_price, price1, price2, price3, prob1, prob2, prob3):
    change1 = (price1-original_price) / original_price
    change2 = (price2-original_price) / original_price
    change3 = (price3-original_price) / original_price
    target_change = change1 * prob1 + change2 * prob2 + change3 * prob3
    latest_change = (latest_price-original_price) / original_price
    
    error = ((change1-latest_change)**2)*prob1 + ((change2-latest_change)**2) *prob2 + ((change3-latest_change)**2)*prob3
    return round(error / abs(target_change), 2)


def add_report(request):
    post_dict = request.POST
    
    stockPrice_df = pd.DataFrame(list(StockPrice.objects.all().values()))
    #以資料庫最新的價格在首頁展示（FB、MSFT）
    fb_latest_price = round((stockPrice_df["fb"]).iloc[-1], 2)
    msft_latest_price = round((stockPrice_df["msft"]).iloc[-1], 2)
    tsla_latest_price = round((stockPrice_df["tsla"]).iloc[-1], 2)
    latest_date = (stockPrice_df["date"]).iloc[-1]
    latest_date = latest_date.strftime("%Y-%m-%d")
    
    report_df = pd.DataFrame(list(Report.objects.all().values()))
    id = report_df['id'].iloc[-1] + 1
    
    name = post_dict["name"]
    stockname = post_dict["stock"]
    date = post_dict["date"]
    price1 = post_dict["price1"]
    predProb1 = post_dict["prediction1"]
    price2 = post_dict["price2"]
    predProb2 = post_dict["prediction2"]
    price3 = post_dict["price3"]
    predProb3 = post_dict["prediction3"]
    content = post_dict["content"]
    
    Report.objects.create(id = id, name = name, stockname = stockname, date = date, price1 = price1, probability1 = predProb1, price2 = price2, probability2 = predProb2, price3 = price3, probability3 = predProb3, content = content)
    return render(request, 'index.html', locals())

def add_report_page(request):
    return render(request, 'add_data.html', locals())

def delete_report(request):
    post_dict = request.POST
    
    id = post_dict["id"]
    name = post_dict["reporter"]
    stockname = post_dict["stock"]
    date = post_dict["date"]
    price1 = post_dict["price1"]
    predProb1 = post_dict["prediction1"]
    price2 = post_dict["price2"]
    predProb2 = post_dict["prediction2"]
    price3 = post_dict["price3"]
    predProb3 = post_dict["prediction3"]
    content = post_dict["content"]

    report = Report.objects.get(id = id, name = name, stockname = stockname, date = date, price1 = price1, probability1 = predProb1, price2 = price2, probability2 = predProb2, price3 = price3, probability3 = predProb3, content = content)
    report.delete()
    
    return render(request, 'index.html', locals())