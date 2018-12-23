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
from django.db.models import Q


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
        results = models.message.objects.all()
        news=[]
        dic = {0:'分配',1:'会签',2:'定稿',3:'审批',4:'签订'}
        for result in results:
            news.append(
                {
                    'id':result.id,
                    'contractnum': result.contractnum.contractnum,
                    'missionnum': result.missionnum,
                    'mission': dic[result.missionnum],
                }
            )
        return JsonResponse(
            {
                'fun1': user_models.role.fun1,
                'fun2': user_models.role.fun2,
                'fun3': user_models.role.fun3,
                'fun4': user_models.role.fun4,
                'fun5': user_models.role.fun5,
                'fun6': user_models.role.fun6,
                'news': news
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
        if request.POST.get("type") =="draft":
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


            return HttpResponse('')
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
            if (request.FILES.get("file", "")):
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



def myManageContract(request):
    if request.method == "POST":
        type = request.POST.get("type")
        if type == "init":
            user = models.MyUser.objects.get(username = get_user(request).username)
            results = models.Administration.objects.filter(
                Q(countersign1=user)|Q(countersign2=user)|Q(countersign3=user)|
                Q(approval1=user) | Q(approval2=user) | Q(approval3=user) |
                Q(sign=user)
            )
            contracts = []
            dic = {'0': '待分配', '1': '会签中', '2': '定稿中', '3': '审批中', '4': '签订中', '5': '签订完成'}
            for result_ in results:
                contract = {}
                result = result_.contractnum
                contract["contractnum"] = result.contractnum
                contract["contractname"] = result.contractname
                contract['draft'] = result.draft.username
                clientname = result.clientnum.clientname if result.clientnum else '(客户已被删除)'
                contract['clientname'] = clientname
                contract['begintime'] = result.begintime.__str__()
                contract['endtime'] = result.endtime.__str__()
                contract['state'] = dic.get(result.state.__str__())
                contract['stateNum'] = result.state.__str__()
                contract['content'] = result.content
                contract['file'] = 'true' if result.file else 'false'

                if result_.countersign1==user:
                    contract_1 = contract.copy()
                    contract_1['myMissionNum'] = '1'
                    contract_1['myMission'] = '会签'
                    if result.state.__str__() < contract_1['myMissionNum']:
                        contract_1['myMissionStateNum'] = '-1'
                        contract_1['myMissionState'] = '待处理'
                    elif result.state.__str__() == contract_1['myMissionNum'] and not result_.copinion1:
                        contract_1['myMissionStateNum'] = '0'
                        contract_1['myMissionState'] = '可处理'
                    else:
                        contract_1['myMissionStateNum'] = '1'
                        contract_1['myMissionState'] = '已处理'
                    contracts.append(contract_1)
                elif result_.countersign2==user:
                    contract_1 = contract.copy()
                    contract_1['myMissionNum'] = '1'
                    contract_1['myMission'] = '会签'
                    if result.state.__str__() < contract_1['myMissionNum']:
                        contract_1['myMissionStateNum'] = '-1'
                        contract_1['myMissionState'] = '待处理'
                    elif result.state.__str__() == contract_1['myMissionNum'] and not result_.copinion2:
                        contract_1['myMissionStateNum'] = '0'
                        contract_1['myMissionState'] = '可处理'
                    else:
                        contract_1['myMissionStateNum'] = '1'
                        contract_1['myMissionState'] = '已处理'
                    contracts.append(contract_1)
                else:
                    contract_1 = contract.copy()
                    contract_1['myMissionNum'] = '1'
                    contract_1['myMission'] = '会签'
                    if result.state.__str__() < contract_1['myMissionNum']:
                        contract_1['myMissionStateNum'] = '-1'
                        contract_1['myMissionState'] = '待处理'
                    elif result.state.__str__() == contract_1['myMissionNum'] and not result_.copinion3:
                        contract_1['myMissionStateNum'] = '0'
                        contract_1['myMissionState'] = '可处理'
                    else:
                        contract_1['myMissionStateNum'] = '1'
                        contract_1['myMissionState'] = '已处理'
                    contracts.append(contract_1)

                if result_.approval1==user:
                    contract_2 = contract.copy()
                    contract_2['myMissionNum'] = '3'
                    contract_2['myMission'] = '审批'
                    if result.state.__str__() < contract_2['myMissionNum']:
                        contract_2['myMissionStateNum'] = '-1'
                        contract_2['myMissionState'] = '待处理'
                    elif result.state.__str__() == contract_2['myMissionNum'] and not result_.aopinion1:
                        contract_2['myMissionStateNum'] = '0'
                        contract_2['myMissionState'] = '可处理'
                    else:
                        contract_2['myMissionStateNum'] = '1'
                        contract_2['myMissionState'] = '已处理'
                    contracts.append(contract_2)
                elif result_.approval2==user:
                    contract_2 = contract.copy()
                    contract_2['myMissionNum'] = '3'
                    contract_2['myMission'] = '审批'
                    if result.state.__str__() < contract_2['myMissionNum']:
                        contract_2['myMissionStateNum'] = '-1'
                        contract_2['myMissionState'] = '待处理'
                    elif result.state.__str__() == contract_2['myMissionNum'] and not result_.aopinion2:
                        contract_2['myMissionStateNum'] = '0'
                        contract_2['myMissionState'] = '可处理'
                    else:
                        contract_2['myMissionStateNum'] = '1'
                        contract_2['myMissionState'] = '已处理'
                    contracts.append(contract_2)
                else:
                    contract_2 = contract.copy()
                    contract_2['myMissionNum'] = '3'
                    contract_2['myMission'] = '审批'
                    if result.state.__str__() < contract_2['myMissionNum']:
                        contract_2['myMissionStateNum'] = '-1'
                        contract_2['myMissionState'] = '待处理'
                    elif result.state.__str__() == contract_2['myMissionNum'] and not result_.aopinion3:
                        contract_2['myMissionStateNum'] = '0'
                        contract_2['myMissionState'] = '可处理'
                    else:
                        contract_2['myMissionStateNum'] = '1'
                        contract_2['myMissionState'] = '已处理'
                    contracts.append(contract_2)

                if result_.sign==user:
                    contract_3 = contract.copy()
                    contract_3['myMissionNum'] = '4'
                    contract_3['myMission'] = '签订'
                    if result.state.__str__() < contract_3['myMissionNum']:
                        contract_3['myMissionStateNum'] = '-1'
                        contract_3['myMissionState'] = '待处理'
                    elif result.state.__str__() == contract_3['myMissionNum']:
                        contract_3['myMissionStateNum'] = '0'
                        contract_3['myMissionState'] = '可处理'
                    else:
                        contract_3['myMissionStateNum'] = '1'
                        contract_3['myMissionState'] = '已处理'
                    contracts.append(contract_3)
            return JsonResponse({'contracts':contracts})
        if type =="countersign":
            user = models.MyUser.objects.get(username=get_user(request).username)
            contractnum = request.POST.get("contractnum")
            copinion = request.POST.get("copinion")
            administration = models.Administration.objects.get(contractnum = models.Contract.objects.get(contractnum=contractnum))
            end = False
            if administration.countersign1 == user:
                administration.ctime1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                administration.copinion1 = copinion
                administration.chas += 1
                if administration.chas == administration.call:
                    end=True
            elif administration.countersign2 == user:
                administration.ctime2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                administration.copinion2 = copinion
                administration.chas += 1
                if administration.chas == administration.call:
                    end = True
            elif administration.countersign3 == user:
                administration.ctime3 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                administration.copinion3 = copinion
                administration.chas += 1
                if administration.chas == administration.call:
                    end = True
            if end == True:
                contract = models.Contract.objects.get(contractnum=contractnum)
                contract.state = 2
                contract.save()
            administration.save()
            return HttpResponse('')
        if type =="approval":
            user = models.MyUser.objects.get(username=get_user(request).username)
            contractnum = request.POST.get("contractnum")
            astate = request.POST.get("astate")
            aopinion = request.POST.get("aopinion")
            administration = models.Administration.objects.get(contractnum = models.Contract.objects.get(contractnum=contractnum))
            if astate == 'false':
                administration.contractnum.state=-1
                administration.save()
                return HttpResponse('')
            end = False
            if administration.approval1 == user:
                administration.atime1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                administration.astate1 = 2
                administration.aopinion1 = aopinion
                administration.ahas += 1
                if administration.ahas == administration.aall:
                    end = True
            elif administration.approval2 == user:
                administration.atime2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                administration.astate2 = 2
                administration.aopinion2 = aopinion
                administration.ahas += 1
                if administration.ahas == administration.aall:
                    end = True
            elif administration.approval3 == user:
                administration.atime3 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                administration.astate3 = 2
                administration.ahas += 1
                if administration.ahas == administration.aall:
                    end = True
            if end == True:
                contract = models.Contract.objects.get(contractnum=contractnum)
                contract.state = 4
                contract.save()
            administration.save()
            return HttpResponse('')
        if type =="sign":
            contractnum = request.POST.get("contractnum")
            sinformation = request.POST.get("sinformation")
            administration = models.Administration.objects.get(
                contractnum=models.Contract.objects.get(contractnum=contractnum))
            administration.sinformation = sinformation
            contract = models.Contract.objects.get(contractnum=contractnum)
            contract.state = 5
            contract.save()
            administration.save()
            return HttpResponse('')
    else:
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
            administration.call=1
            mail(administration.countersign1.email,'尊敬的用户您好！ 您需要会签一份合同，请及时登录查看！')
            message1 = models.message(username=administration.countersign1,contractnum=contract,missionnum=1)
            message1.save()
            if countersign2:
                administration.call = 2
                administration.countersign2 = models.MyUser.objects.get(username=countersign2)
                mail(administration.countersign2.email, '尊敬的用户您好！ 您需要会签一份合同，请及时登录查看！')
                message2 = models.message(username=administration.countersign2, contractnum=contract, missionnum=1)
                message2.save()
            if countersign3:
                administration.call = 3
                administration.countersign3 = models.MyUser.objects.get(username=countersign3)
                mail(administration.countersign3.email, '尊敬的用户您好！ 您需要会签一份合同，请及时登录查看！')
                message3 = models.message(username=administration.countersign3, contractnum=contract, missionnum=1)
                message3.save()

            administration.approval1 = models.MyUser.objects.get(username=approval1)
            mail(administration.approval1.email, '尊敬的用户您好！ 您需要审核一份合同，请及时登录查看！')
            message4 = models.message(username=administration.approval1, contractnum=contract, missionnum=3)
            message4.save()
            administration.aall = 1
            if approval2:
                administration.aall = 2
                administration.approval2 = models.MyUser.objects.get(username=approval2)
                mail(administration.approval2.email, '尊敬的用户您好！ 您需要审核一份合同，请及时登录查看！')
                message5 = models.message(username=administration.approval2, contractnum=contract, missionnum=3)
                message5.save()
            if approval3:
                administration.aall = 3
                administration.approval3 = models.MyUser.objects.get(username=approval3)
                mail(administration.approval3.email, '尊敬的用户您好！ 您需要审核一份合同，请及时登录查看！')
                message6 = models.message(username=administration.approval3, contractnum=contract, missionnum=3)
                message6.save()
            administration.sign = models.MyUser.objects.get(username=sign)
            administration.save()
            mail(administration.sign.email, '尊敬的用户您好！ 您需要签订一份合同，请及时登录查看！')
            message7 = models.message(username=administration.sign, contractnum=contract, missionnum=4)
            message7.save()
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
    if request.method == "POST":
        if request.POST.get("type") == "init":
            dic = {'0': '待分配', '1': '会签中', '2': '定稿中', '3': '审批中', '4': '签订中', '5': '签订完成'}
            results = models.Contract.objects.all()
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
            return JsonResponse({'contracts': contracts})
    else:
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
    if request.method == "POST":
        type = request.POST.get('type')
        if type == "init":
            user_model = models.MyUser.objects.get(username=get_user(request).username)
            results = models.Client.objects.filter(username=user_model)
            clients = []
            for result in results:
                client = {
                    'clientnum': result.clientnum,
                    'clientname': result.clientname,
                    'tel': result.tel,
                    'fax': result.fax,
                    'address': result.address,
                    'code': result.code,
                    'bank': result.bank,
                    'account': result.account,
                    'addition': result.addition,
                }
                clients.append(client)
            return JsonResponse({'clients':clients})
        if type == "add":
            client = models.Client()
            client.clientname = request.POST.get("clientname")
            client.tel = request.POST.get("tel")
            client.fax = request.POST.get("fax")
            client.address = request.POST.get("address")
            client.code = request.POST.get("code")
            client.bank = request.POST.get("bank")
            client.account = request.POST.get("account")
            client.addition = request.POST.get("addition")
            client.username = models.MyUser.objects.get(username=get_user(request).username)
            client.save()
            return HttpResponse("")
        if type == "delete":
            client = models.Client.objects.get(clientnum=request.POST.get("clientnum"))
            client.delete()
            return HttpResponse('')

    return render(request, 'myClient.html')


def allClient(request):
    if request.method == "POST":
        type = request.POST.get('type')
        if type == 'init':
            results = models.Client.objects.all()
            clients=[]
            for result in results:
                client={
                    'clientnum': result.clientnum,
                    'clientname': result.clientname,
                    'tel': result.tel,
                    'fax': result.fax,
                    'address': result.address,
                    'code': result.code,
                    'bank': result.bank,
                    'account': result.account,
                    'addition': result.addition,
                    'username':result.username.username
                }
                clients.append(client)
            return JsonResponse({"clients":clients})
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

def news(request):
    if request.method == "POST":
        if(request.POST.get("type")=="delete"):
            message = models.message.objects.get(id=request.POST.get('id'))
            message.delete()
            return HttpResponse('')