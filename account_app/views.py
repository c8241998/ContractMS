from django.contrib import auth
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from account_app import models
import time
import json
# Create your views here.
def add(request):
    # if request.method == "POST":
    res = {'msg': 'success'}
    return HttpResponse(json.dumps(res))

def query(request):
    if request.method == "GET":
        res = {'msg': 'success'}
        return HttpResponse(json.dumps(res))

def home(request):
    user = get_user(request)
    if user.is_anonymous:
        return render(request,'landing.html')
    else:
        return redirect('manage')

# Create your views here.
def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            re = models.MyUser.objects.get(email=email)
        except models.MyUser.DoesNotExist:
            res = {'msg': 'fail','info':'email not found.'}
            return HttpResponse(json.dumps(res))
        re = auth.authenticate(request, username=email, password=password)
        if re is None:
            res = {'msg': 'fail', 'info': 'password is invalid.'}
            return HttpResponse(json.dumps(res))
        auth.login(request,re)
        res = {'msg':'success'}
        return HttpResponse(json.dumps(res))
    return render(request, 'login.html');


def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        try:
            re = models.MyUser.objects.get(email=email)
            res = {'msg': 'fail','info':'email already taken.'}
            return HttpResponse(json.dumps(res))
        except models.MyUser.DoesNotExist:
            try:
                re = models.MyUser.objects.get(username=username)
                res = {'msg': 'fail', 'info': 'username already taken.'}
                return HttpResponse(json.dumps(res))
            except models.MyUser.DoesNotExist:
                user = models.MyUser()
                user.email = email
                user.set_password(password)
                user.username = username
                user.created_at = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                user.save()
                res = {'msg': 'success'}
                return HttpResponse(json.dumps(res))
    return render(request, 'register.html')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')

def manage(request):
    return render(request,'manage.html')