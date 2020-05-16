# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_auto_20200516_1055'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indexgoodsbanner',
            name='sku',
        ),
    ]
