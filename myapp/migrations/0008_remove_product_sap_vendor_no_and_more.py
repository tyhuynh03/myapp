# Generated by Django 5.1 on 2024-11-17 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_product_date_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='SAP_Vendor_No',
        ),
        migrations.RemoveField(
            model_name='product',
            name='so_chung_nhan',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tinh_trang',
        ),
        migrations.RemoveField(
            model_name='product',
            name='tinh_trang_bao_cao',
        ),
    ]
