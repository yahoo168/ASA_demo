"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from restaurants.views import here, add
from mysite.views import login, index, logout, register, keyword_search, show_homepage_index, add_report, delete_report
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', index),
    path('accounts/login/', login),
    path('accounts/login/login', login),
    path('accounts/logout/', logout),
    path('accounts/register/', register),
    path('index/', keyword_search),
    path('index/', show_homepage_index),
    path('add_data/', add_report),
    path('index/', delete_report)
]
