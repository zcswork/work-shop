from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib.auth import authenticate,login
from django.http import HttpResponse
from django.conf import settings
from user.models import User
from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from utils.mixin import LoginRequireMixin
import re

class RegisterView(View):
    '''注册'''
    def get(self,request):
        '''显示注册页面'''
        return render(request, 'register.html')
    def post(self,request):
        '''进行注册处理'''
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 检验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        #发送激活邮件,包含激活链接：http://127.0.0.1:8000/user/active/3
        #激活链接需要包括用户身份信息,并且要把身份信息加密

        #加密用户身份信息，生成激活token
        serializer=Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info) #bytes
        token = token.decode()

        #发邮件
        send_register_active_email.delay(email,username,token)

        # 返回应答
        return redirect(reverse('user:login'))

class ActiveView(View):
    '''用户激活'''
    def get(self,request,token):
        '''进行用户激活'''
        # print(token)
        #进行解密，获取要激活的用户信息
        serializer=Serializer(settings.SECRET_KEY,3600)
        try:
            info = serializer.loads(bytes(token,encoding='utf-8'))
            #获取待激活用户的id
            user_id = info['confirm']

            #根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            #跳转到登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            #激活链接已过期
            return HttpResponse('激活链接已过期')

class LoginView(View):
    '''登录'''
    def get(self,request):
        '''显示登录页面'''
        #判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        #使用模板
        return render(request,'login.html',{'username':username,'checked':checked})
    def post(self,request):
        '''登录校验'''
        #接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        #校验数据
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'数据不完整'})

        #业务处理：登录校验
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                #用户已激活
                #记录用户的登录状态
                login(request,user)
                #获取登录后所要跳转到的地址
                #默认跳到首页
                next_url = request.GET.get('next',reverse('goods:index'))
                #跳转到首页
                response = redirect(next_url)
                #判断是否需要记住用户名
                remember = request.POST.get('remember')
                if remember == 'on':
                    #记住用户名
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                #用户未激活
                return render(request,'login.html',{'errmsg':'账户未激活'})
        else:
            #用户名或密码错误
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})

class UserInfoView(LoginRequireMixin,View):
    '''用户中心-信息页'''
    def get(self,request):
        '''显示'''
        return render(request,'user_center_info.html',{'page':'user'})


class UserOrderView(LoginRequireMixin,View):
    '''用户中心-订单页'''
    def get(self, request):
        '''显示'''
        return render(request, 'user_center_order.html',{'page':'order'})

class AddressView(LoginRequireMixin,View):
    '''用户中心-地址页'''
    def get(self, request):
        '''显示'''
        return render(request, 'user_center_site.html',{'page':'address'})


