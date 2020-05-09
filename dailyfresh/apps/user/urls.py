from django.conf.urls import include, url
from user import views

urlpatterns = [
    url(r'^register/$',views.register,name='register'), #注册
    url(r'^login/$',views.login,name='login'), #登录
]
