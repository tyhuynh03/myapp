# Generated by Django 5.1 on 2024-10-03 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='ngay_het_hieu_luc',
            field=models.CharField(max_length=50),
        ),
    ]
