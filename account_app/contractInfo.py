from account_app import models

def getContractInfo(contractnum):

    dic={2:'通过',1:'拒绝',0:'未审批'}

    contract = models.Contract.objects.get(contractnum=contractnum)
    administration = models.Administration.objects.get(contractnum=contract)
    cInfo = {}
    cInfo['contractnum'] = contractnum

    cInfo['countersign1'] = administration.countersign1.username if administration.countersign1 else "无"
    cInfo['countersign2'] = administration.countersign2.username if administration.countersign2 else "无"
    cInfo['countersign3'] = administration.countersign3.username if administration.countersign3 else "无"

    cInfo['copinion1'] = administration.copinion1 if administration.copinion1 else "无"
    cInfo['copinion2'] = administration.copinion2 if administration.copinion2 else "无"
    cInfo['copinion3'] = administration.copinion3 if administration.copinion3 else "无"

    cInfo['ctime1'] = administration.ctime1.__str__() if administration.ctime1 else "无"
    cInfo['ctime2'] = administration.ctime2.__str__() if administration.ctime2 else "无"
    cInfo['ctime3'] = administration.ctime3.__str__() if administration.ctime3 else "无"

    cInfo['approval1'] = administration.approval1.username if administration.approval1 else "无"
    cInfo['approval2'] = administration.approval2.username if administration.approval2 else "无"
    cInfo['approval3'] = administration.approval3.username if administration.approval3 else "无"

    cInfo['astate1'] = dic[administration.astate1] if administration.astate1 else "无"
    cInfo['astate2'] = dic[administration.astate2] if administration.astate2 else "无"
    cInfo['astate3'] = dic[administration.astate3] if administration.astate3 else "无"

    cInfo['atime1'] = administration.atime1.__str__() if administration.atime1 else "无"
    cInfo['atime2'] = administration.atime2.__str__() if administration.atime2 else "无"
    cInfo['atime3'] = administration.atime3.__str__() if administration.atime3 else "无"

    cInfo['aopinion1'] = administration.aopinion1 if administration.aopinion1 else "无"
    cInfo['aopinion2'] = administration.aopinion2 if administration.aopinion2 else "无"
    cInfo['aopinion3'] = administration.aopinion3 if administration.aopinion3 else "无"

    cInfo['sign'] = administration.sign.username if administration.sign else "无"
    cInfo['sinformation'] = administration.sinformation if administration.sinformation else "无"
    cInfo['stime'] = administration.stime.__str__() if administration.stime else "无"

    return cInfo