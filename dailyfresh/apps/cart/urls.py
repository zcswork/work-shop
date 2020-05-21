from django.conf.urls import include, url
from cart.views import CartAddView,CartInfoView,CartUpdateView,CartDeleteView
from cart.views import CartAddView,CartInfoView


urlpatterns = [
    url(r'^add$',CartAddView.as_view(),name='add'),#购物车记录添加
    url(r'^$',CartInfoView.as_view(),name='show'),#购物车页面显示
    url(r'^update$',CartUpdateView.as_view(),name='update'),#购物车记录更新
    url(r'^delete$',CartDeleteView.as_view(),name='delete'),#购物车删除
]

