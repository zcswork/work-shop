# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodsimage',
            name='image',
            field=models.ImageField(verbose_name='图片路径', upload_to='cars/'),
        ),
        migrations.AlterField(
            model_name='goodssku',
            name='image',
            field=models.ImageField(verbose_name='商品图片', upload_to='cars/'),
        ),
        migrations.AlterField(
            model_name='goodstype',
            name='image',
            field=models.ImageField(verbose_name='商品类型图片', upload_to='cars/'),
        ),
        migrations.AlterField(
            model_name='indexgoodsbanner',
            name='image',
            field=models.ImageField(verbose_name='图片', upload_to='cars/'),
        ),
        migrations.AlterField(
            model_name='indexpromotionbanner',
            name='image',
            field=models.ImageField(verbose_name='图片', upload_to='cars/'),
        ),
    ]
