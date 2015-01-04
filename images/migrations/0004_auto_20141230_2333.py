# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_image_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='hash',
            field=models.CharField(unique=True, max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
