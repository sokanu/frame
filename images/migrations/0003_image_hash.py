# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_image_content_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='hash',
            field=models.BigIntegerField(default=0, unique=True, max_length=255, blank=True),
            preserve_default=False,
        ),
    ]
