"""ContractMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
# from django.urls import path
from account_app import views
from django.conf.urls import include, url

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'admin/', admin.site.urls),
    url(r'^login$', views.login, name='login'),
    url(r'^register$', views.register, name='register'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^$', views.home, name='home'),
    url(r'^manage$', views.manage, name='manage'),
    url(r'^myContract$', views.myContract, name='myContract'),
    url(r'^newContract$', views.newContract, name='newContract'),
    url(r'^myManageContract$', views.myManageContract, name='myManageContract'),
    url(r'^setContract$', views.setContract, name='setContract'),
    url(r'^allContract$', views.allContract, name='allContract'),
    url(r'^role$', views.role, name='role'),
    url(r'^user$', views.user, name='user'),
    url(r'^myClient$', views.myClient, name='myClient'),
    url(r'^allClient$', views.allClient, name='allClient'),
    url(r'^log$', views.log, name='log'),
    url(r'^downloadFile$', views.downloadFile, name='downloadFile'),

    url(r'^add$', views.add, name='add'),
    url(r'^query$', views.query, name='query'),
]
