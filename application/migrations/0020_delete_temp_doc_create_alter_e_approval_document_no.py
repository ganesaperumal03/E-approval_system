# Generated by Django 5.0.6 on 2024-06-25 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0019_rename_attachment_temp_doc_create_temp_attachment_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='temp_doc_create',
        ),
        migrations.AlterField(
            model_name='e_approval',
            name='Document_no',
            field=models.CharField(max_length=500, primary_key=True, serialize=False),
        ),
    ]