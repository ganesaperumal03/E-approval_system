# Generated by Django 5.0.4 on 2024-06-21 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0015_e_approval_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='e_approval',
            name='GM_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='e_approval',
            name='HOD_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='e_approval',
            name='Staff_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='e_approval',
            name='principal_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='e_approval',
            name='vp_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
