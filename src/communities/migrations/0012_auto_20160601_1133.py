# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-01 08:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0011_auto_20150615_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitygroup',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='communities.Community', verbose_name='Community'),
        ),
        migrations.AlterField(
            model_name='communitygroup',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='communitygrouprole',
            name='committee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_roles', to='communities.Committee', verbose_name='Committee'),
        ),
        migrations.AlterField(
            model_name='communitygrouprole',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_roles', to='communities.CommunityGroup', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='communitygrouprole',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_roles', to='acl.Role', verbose_name='Role'),
        ),
    ]
