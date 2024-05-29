# Generated by Django 5.0.1 on 2024-05-28 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_auth_list_auth_remarks_clarification_doc_remarks_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='auth_list',
            name='staff',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='auth_list',
            name='staff_clarification',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='auth_list',
            name='staff_date',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='auth_list',
            name='staff_reason',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='auth_list',
            name='staff_remarks',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='e_approval',
            name='Staff',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='e_approval',
            name='Staff_date',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]