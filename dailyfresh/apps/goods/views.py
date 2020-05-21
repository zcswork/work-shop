from django.shortcuts import render,redirect
from django.views.generic import View
from django.core.urlresolvers import reverse
from goods.models import GoodsType,GoodsSKU,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from order.models import OrderGoods
from django_redis import get_redis_connection
from django.core.paginator import Paginator

class IndexView(View):
    '''首页'''
    def get(self,request):
        '''显示首页'''
        #获取商品的种类信息
        types = GoodsType.objects.all()

        #获取首页轮播商品信息
        goods_banners = IndexGoodsBanner.objects.all().order_by('index')

        #获取首页促销活动信息
        promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

        #获取首页分类商品展示信息
        for type in types:
            #获取type种类首页分类商品的图片展示信息
            image_banners = IndexTypeGoodsBanner.objects.all().filter(type=type,display_type=1).order_by('index')[0:4]
            #获取type种类首页分类商品的文字展示信息
            title_banners = IndexTypeGoodsBanner.objects.all().filter(type=type,display_type=0).order_by('index')[0:4]

            #动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
            type.image_banners = image_banners
            type.title_banners = title_banners
            # print(image_banners)
            # print(title_banners)
            print(image_banners)
            print(title_banners)

        #获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            #用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' %user.id
            cart_count = conn.hlen(cart_key)

        #组织模板上下文
        context = {'types':types,
                   'goods_banners':goods_banners,
                   'promotion_banners':promotion_banners,
                   'cart_count':cart_count}

        #使用模板
        return render(request,'index.html',context)

class DetailView(View):
    '''详情页'''
    def get(self,request,goods_id):
        '''显示详情页'''
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return redirect(reverse('goods:index'))

        #获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        #获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[0:2]

        #获取同一个SPU的其他规格的商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            #添加历史浏览记录
            conn = get_redis_connection('default')
            history_key = 'history_%d'%user.id
            #移除列表的goods_id
            conn.lrem(history_key,0,goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key,goods_id)
            #只保存用户最新浏览的5条信息
            conn.ltrim(history_key,0,4)

        #组织模板上下文
        context = {'sku':sku,
                   'types':types,
                   'sku_orders':sku_orders,
                   'new_skus':new_skus,
                   'cart_count':cart_count,
                   'same_spu_skus':same_spu_skus
                   }
        #使用模板
        return render(request,'detail.html',context)

class ListView(View):
    '''列表页'''
    def get(self,request,type_id,page):
        '''显示列表页'''
        #获取种类信息
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            #种类不存在
            return redirect(reverse('goods:index'))
        # 获取商品的分类信息
        types = GoodsType.objects.all().filter()

        types = GoodsType.objects.all()
        #获取排序的方式
        #sort=default 按照默认id排序
        #sort=price 按照价格排序
        #sort=hot 按照销量排序
        sort = request.GET.get('sort')

        if sort == 'price':
            skus = GoodsSKU.objects.all().filter(type=type).order_by('price')
        elif sort == 'hot':
            skus = GoodsSKU.objects.all().filter(type=type).order_by('-sales')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.all().filter(type=type).order_by('-id')

        #对数据进行分页
        paginator = Paginator(skus,1)

        #获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1


        #获取第page页的Page实例对象
        skus_page = paginator.page(page)

        # 进行页码的控制，页面最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，页面上显示1-5页
        # 3.如果当前页是后3页，页面上显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页后2页
        num_page = paginator.num_pages
        if num_page < 5:
            pages = range(1,num_page+1)
        elif page <= 3:
            pages = range(1,6)
        elif num_page - page <=2:
            pages = range(num_page-4,num_page+1)
        else:
            pages = range(page-2,page+3)

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[0:2]

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        #组织模板上下文
        context = {'type':type,'types':types,
                   'skus_page':skus_page,
                   'new_skus':new_skus,
                   'cart_count':cart_count,
                   'sort':sort,'pages':pages

                   }

        return render(request,'list.html',context)
