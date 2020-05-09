from django.shortcuts import render

def register(request):
    '''显示注册页面'''
    return render(request,'register.html')
def login(request):
    '''显示登录页面'''
    return render(request,'login.html')
