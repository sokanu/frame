# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_auto_20141230_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='path',
            field=models.CharField(default='', max_length=1024),
            preserve_default=False,
        ),
    ]
