from django.contrib import auth
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from account_app import models
import time
import json
from django.http import FileResponse

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
        return render(request, 'landing.html')
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
            res = {'msg': 'fail', 'info': 'email not found.'}
            return HttpResponse(json.dumps(res))
        re = auth.authenticate(request, username=email, password=password)
        if re is None:
            res = {'msg': 'fail', 'info': 'password is invalid.'}
            return HttpResponse(json.dumps(res))
        auth.login(request, re)
        res = {'msg': 'success'}
        return HttpResponse(json.dumps(res))
    return render(request, 'login.html');


def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')
        try:
            re = models.MyUser.objects.get(email=email)
            res = {'msg': 'fail', 'info': 'email already taken.'}
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

@login_required
def manage(request):
    return render(request, 'manage.html')


def myContract(request):
    if request.method == "POST":
        dic = {'0':'待分配','1':'会签中','2':'定稿中','3':'审批中','4':'签订中','5':'签订完成'}
        user = get_user(request)
        user_models = models.MyUser.objects.get(email=user.email)
        results = models.Contract.objects.filter(draft=user_models)
        contracts = []

        for result in results:
            contract = {}
            contract["contractnum"] = result.contractnum
            contract["contractname"] = result.contractname
            contract['clientname'] = result.clientnum.clientname
            contract['begintime'] = result.begintime.__str__()
            contract['endtime'] = result.endtime.__str__()
            contract['state'] = dic.get(result.state.__str__())
            contract['stateNum'] = result.state
            contract['draft'] = result.draft.username
            contract['content'] = result.content
            contract['file'] =  'true' if result.file else 'false'
            contracts.append(contract)
        json_ = {'contracts': contracts}
        return HttpResponse(json.dumps(json_))

    else:
        clients = models.Client.objects.all()
        res=[]
        for client in clients:
            res.append(client.clientname)
        json_={'clients':res}
        return render(request,"mycontract.html",json_)

def setContract(request):
    return render(request, 'setcontract.html')

def newContract(request):
    if request.method == "POST":
        contractname = request.POST.get("contractname")
        # clientname = request.POST.get("clientname")
        clientname = models.Client.objects.get(clientname=request.POST.get("clientname"))
        begintime = request.POST.get("begintime")
        endtime = request.POST.get("endtime")

        content = request.POST.get("content")
        file = request.FILES.get("file", "")
        user = get_user(request)
        user_models = models.MyUser.objects.get(email=user.email)
        contract = models.Contract(contractname=contractname, clientnum=clientname, begintime=begintime,
                                   endtime=endtime, content=content, file=file, draft=user_models)
        contract.save()
        msg = {'msg': 'success'}
        return HttpResponse(json.dumps(msg))

def myManageContract(request):
    return render(request, 'myManageContract.html')

def setContract(request):
    return render(request, 'setContract.html')

def allContract(request):
    return render(request, 'allContract.html')

def role(request):
    return render(request, 'role.html')

def user(request):
    return render(request, 'user.html')

def myClient(request):
    return render(request, 'myClient.html')

def allClient(request):
    return render(request, 'allClient.html')

def log(request):
    return render(request, 'log.html')

def downloadFile(request):
    if request.method == "POST":
        contractnum = request.POST.get('contractnum')
        file = models.Contract.objects.get(contractnum=contractnum).file
        file_=open('media/' + file.name, 'rb')
        response = FileResponse(file_)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="'+file.name+'"'

        return response
