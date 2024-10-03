from django.db import models

class Product(models.Model):
    article = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    barcode = models.CharField(max_length=50)
    date_created = models.CharField(max_length=50)   
    SAP_Vendor_No = models.CharField(max_length=50)
    Vendor = models.CharField(max_length=200)
    so_chung_nhan = models.CharField(max_length=50)
    ngay_het_hieu_luc = models.CharField(max_length=50)
    tinh_trang = models.CharField(max_length=50)
    tinh_trang_bao_cao = models.CharField(max_length=50)
    ma_ho_so = models.CharField(max_length=50)
    def __str__(self):
        return self.article
# Compare this snippet from myapp/migrations/0001_initial.py:
# from django.db import migrations, models
#