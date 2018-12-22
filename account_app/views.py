from django.contrib import auth
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from account_app import models
import time
import json
from django.http import FileResponse
from django.http import JsonResponse
from .mailSender import *
from .contractInfo import *


# Create your views here.

def home(request):
    user = get_user(request)
    if user.is_anonymous:
        return render(request, 'landing.html')
    else:
        return redirect("manage")


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

        mail("shxy522@outlook.com", "登陆成功!", "合同管理系统", "czd", "登陆成功提示")

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
    user = get_user(request)
    username = user.username
    if request.method == "POST":
        user_models = models.MyUser.objects.get(username=username)
        return JsonResponse(
            {
                'fun1': user_models.role.fun1,
                'fun2': user_models.role.fun2,
                'fun3': user_models.role.fun3,
                'fun4': user_models.role.fun4,
                'fun5': user_models.role.fun5,
                'fun6': user_models.role.fun6,
            }
        )
    else:
        return render(request, "manage.html", {'username': username})


def myContract(request):
    if request.method == "POST":
        if request.POST.get("type") == "init":
            dic = {'0': '待分配', '1': '会签中', '2': '定稿中', '3': '审批中', '4': '签订中', '5': '签订完成'}
            user = get_user(request)
            user_models = models.MyUser.objects.get(email=user.email)
            results = models.Contract.objects.filter(draft=user_models)
            contracts = []

            for result in results:
                contract = {}
                contract["contractnum"] = result.contractnum
                contract["contractname"] = result.contractname
                clientname = result.clientnum.clientname if result.clientnum else '客户资料已被删除'
                contract['clientname'] = clientname
                contract['begintime'] = result.begintime.__str__()
                contract['endtime'] = result.endtime.__str__()
                contract['state'] = dic.get(result.state.__str__())
                contract['stateNum'] = result.state
                contract['draft'] = result.draft.username
                contract['content'] = result.content
                contract['file'] = 'true' if result.file else 'false'
                contracts.append(contract)
            json_ = {'contracts': contracts}
            return HttpResponse(json.dumps(json_))
        elif request.POST.get("type") == "info":
            contractnum = request.POST.get("contractnum")
            cInfo = getContractInfo(contractnum)
            return JsonResponse({"cInfo": cInfo})
        elif request.POST.get("type") == "finalize":
            contractnum = request.POST.get("contractnum")
            contract = models.Contract.objects.get(contractnum=contractnum)
            contract.contractname = request.POST.get("contractname")
            contract.clientnum = models.Client.objects.get(clientname=request.POST.get("clientname"))
            contract.begintime = request.POST.get("begintime")
            contract.endtime = request.POST.get("endtime")
            contract.content = request.POST.get("content")
            if(request.FILES.get("file", "")):
                contract.file = request.FILES.get("file", "")
            contract.state = 3
            contract.save()
            return HttpResponse('')
    else:
        clients = models.Client.objects.all()
        res = []
        for client in clients:
            res.append(client.clientname)
        json_ = {'clients': res}
        return render(request, "mycontract.html", json_)


def newContract(request):
    if request.method == "POST":
        contractname = request.POST.get("contractname")
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
    if request.method == "POST":
        if (request.POST.get("type") == "init"):

            dic = {'0': '待分配', '1': '会签中', '2': '定稿中', '3': '审批中', '4': '签订中', '5': '签订完成'}
            results = models.Contract.objects.all()
            contracts = []
            for result in results:
                contract = {}
                contract["contractnum"] = result.contractnum
                contract["contractname"] = result.contractname
                clientname = result.clientnum.clientname if result.clientnum else '(客户已被删除)'
                contract['clientname'] = clientname
                contract['begintime'] = result.begintime.__str__()
                contract['endtime'] = result.endtime.__str__()
                contract['state'] = dic.get(result.state.__str__())
                contract['stateNum'] = result.state.__str__()
                contract['draft'] = result.draft.username
                contracts.append(contract)

            results = models.MyUser.objects.filter(role__fun2=True)
            users = []
            for result in results:
                users.append(result.username)

            return JsonResponse({"contracts": contracts, "users": users})

        if (request.POST.get("type") == "distribution"):
            contractnum = request.POST.get("contractnum")
            countersign1 = request.POST.get("countersign1")
            countersign2 = request.POST.get("countersign2")
            countersign3 = request.POST.get("countersign3")
            approval1 = request.POST.get("approval1")
            approval2 = request.POST.get("approval2")
            approval3 = request.POST.get("approval3")
            sign = request.POST.get("sign")

            contract = models.Contract.objects.get(contractnum=contractnum)
            administration = models.Administration()
            administration.contractnum = contract
            administration.countersign1 = models.MyUser.objects.get(username=countersign1)
            if countersign2:
                administration.countersign2 = models.MyUser.objects.get(username=countersign2)
            if countersign3:
                administration.countersign3 = models.MyUser.objects.get(username=countersign3)
            administration.approval1 = models.MyUser.objects.get(username=approval1)
            if approval2:
                administration.approval2 = models.MyUser.objects.get(username=approval2)
            if approval3:
                administration.approval3 = models.MyUser.objects.get(username=approval3)
            administration.sign = models.MyUser.objects.get(username=sign)
            administration.save()

            contract.state = 1
            contract.save()

            return HttpResponse('')

        if (request.POST.get("type") == "info"):
            contractnum = request.POST.get("contractnum")
            cInfo = getContractInfo(contractnum)
            return JsonResponse({'cInfo': cInfo})
    else:
        return render(request, 'setContract.html')


def allContract(request):
    return render(request, 'allContract.html')


def role(request):
    if request.method == "POST":
        type = request.POST.get('type')
        if type == 'addRole':
            role = request.POST.get('role')
            description = request.POST.get('description')
            try:
                temp = models.Role.objects.get(role=role)
                return JsonResponse({"msg": "fail", "info": "角色名已存在"})
            except models.Role.DoesNotExist:
                newRole = models.Role()
                newRole.role = role
                newRole.description = description
                newRole.save()
                return JsonResponse({"msg": "success"})
        elif type == 'init':
            results = models.Role.objects.all()
            roles = []
            for result in results:
                roles.append({'role': result.role, 'description': result.description,
                              'fun1': result.fun1, 'fun2': result.fun2,
                              'fun3': result.fun3, 'fun4': result.fun4,
                              'fun5': result.fun5, 'fun6': result.fun6
                              })
            return JsonResponse({"roles": roles})
        elif type == 'save':
            dic = {"true": True, 'false': False}
            role = request.POST.get('role')
            fun1 = request.POST.get('fun1')
            fun2 = request.POST.get('fun2')
            fun3 = request.POST.get('fun3')
            fun4 = request.POST.get('fun4')
            fun5 = request.POST.get('fun5')
            fun6 = request.POST.get('fun6')
            role_models = models.Role.objects.get(role=role)
            role_models.fun1 = dic[fun1]
            role_models.fun2 = dic[fun2]
            role_models.fun3 = dic[fun3]
            role_models.fun4 = dic[fun4]
            role_models.fun5 = dic[fun5]
            role_models.fun6 = dic[fun6]
            role_models.save()
            return JsonResponse({"msg": "success"})
        elif type == 'delete':
            role = request.POST.get('role')
            role_models = models.Role.objects.get(role=role)
            role_models.delete()
            return JsonResponse({"msg": "success"})
    else:
        return render(request, 'role.html')


def user(request):
    if request.method == "POST":
        type = request.POST.get('type')
        if type == "init":
            results = models.MyUser.objects.all()
            users = []
            for result in results:
                role = result.role.role if result.role else '无'
                users.append({'username': result.username, 'email': result.email, 'role': role})
            return JsonResponse({"users": users})
        elif type == "save":
            username = request.POST.get('username')
            role = request.POST.get('role')
            role_models = models.Role.objects.get(role=role)
            user_models = models.MyUser.objects.get(username=username)
            user_models.role = role_models
            user_models.save()
            return HttpResponse('')
        elif type == "delete":
            username = request.POST.get('username')
            user_models = models.MyUser.objects.get(username=username)
            user_models.delete()
            return HttpResponse('')
    else:
        results = models.Role.objects.all()
        roles = []
        for result in results:
            roles.append(result.role)
        return render(request, 'user.html', {'roles': roles})


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
        file_ = open('media/' + file.name, 'rb')
        response = FileResponse(file_)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="' + file.name + '"'

        return response
