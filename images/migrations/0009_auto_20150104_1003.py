# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0008_s3connection'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='image',
            unique_together=set([('hash', 'variation')]),
        ),
    ]
