from django.shortcuts import *
from crm import models
from rbac.service.init_permission import init_permission
# Create your views here.

def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    user = request.POST.get('user')
    pwd = request.POST.get('pwd')
    user_obj = models.UserInfo.objects.filter(name=user,password=pwd).first()
    if not user_obj:
        return render(request,'login.html',{'msg':'用户名密码错误'})

    #用户密码正确，信息存入session
    request.session['user_info'] = {'id':user_obj.id,'name':user_obj.names}

    #权限信息初始化
    init_permission(user_obj,request)

    return redirect('/stark/crm/course/list/')
