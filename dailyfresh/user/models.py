from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from db.base_model import BaseModel


class User(AbstractUser,BaseModel):
    '''用户模型类'''
    def generate_active_token(self):
        '''生成用户签名字符串'''
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':self.id}
        token = serializer.dumps(info)
        return token.decode()

class Address(AbstractUser,BaseModel):
    '''地址模型类'''
    user = models.ForeignKey('User',verbose_name='所属账户')
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件人地址')
    phone = models.CharField(max_length=11,verbose_name='联系电话')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')

    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name