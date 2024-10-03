import csv
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ValidationError
from .models import Product
import os

def home(request):
    return render(request, 'myapp/upload_xlsx.html') # This renders the home.html template
def upload_xlsx(request):
    if request.method == 'POST':
        print(request.FILES)  # In ra thông tin file
        xlsx_file = request.FILES['file']

        # Đảm bảo file có định dạng XLSX
        if not xlsx_file.name.endswith('.xlsx'):
            return HttpResponse("Không phải định dạng XLSX")

        print("Đang đọc file XLSX...")
        # Đọc dữ liệu từ file XLSX
        data = []
        df = pd.read_excel(xlsx_file)
        df.columns = ['article', 'name', 'barcode', 'date_created', 'SAP_Vendor_No', 'Vendor', 'so_chung_nhan', 'ngay_het_hieu_luc', 'tinh_trang', 'tinh_trang_bao_cao', 'ma_ho_so']
         # Xóa dòng dữ liệu đầu tiên
        df = df.drop(df.index[0])
        # Định dạng ngày tháng
        
        data = df.to_dict(orient='records')
        # Lưu dữ liệu vào model
        for item in data:
            try:
                Product.objects.create(
                    article=item['article'],
                    name=item['name'],
                    barcode=item['barcode'],
                    date_created=item['date_created'],
                    SAP_Vendor_No=item['SAP_Vendor_No'],
                    Vendor=item['Vendor'],
                    so_chung_nhan=item['so_chung_nhan'],
                    ngay_het_hieu_luc=item['ngay_het_hieu_luc'],
                    tinh_trang=item['tinh_trang'],
                    tinh_trang_bao_cao=item['tinh_trang_bao_cao'],
                    ma_ho_so=item['ma_ho_so'],
                )
            except ValidationError:
                pass
        print("Đọc file XLSX thành công!")
        return render(request, 'myapp/read_xlsx.html', {'data': data})

    return render(request, 'myapp/upload_xlsx.html')

def search(request):
    if request.method == 'POST':
        search = request.POST['search']
        print(search)
        products = Product.objects.filter(article__icontains=search)
        return render(request, 'myapp/read_xlsx.html', {'data': products})
    return render(request, 'myapp/read_xlsx.html')

# def find_folder(folder_name, search_path='/app/mydrive'):
#     for drive in os.walk(search_path):
#         for root, dirs, files in os.walk(drive + "\\"):
#             if folder_name in dirs:
#                 return os.path.join(root, folder_name)
#     return None
import os

def find_folder(folder_name, drives = ['C:', 'D:', 'E:', 'F:', 'G:', 'H:', 'I:', 'J:', 'K:', 'L:', 'M:', 'N:', 'O:', 'P:', 'Q:', 'R:', 'S:', 'T:', 'U:', 'V:', 'W:', 'X:', 'Y:', 'Z:']):
    for drive in drives:
        for root, dirs, files in os.walk(drive + "\\"):
            if folder_name in dirs:
                return os.path.join(root, folder_name)
    return None
def open_folder(request,ma_ho_so):
    folder_path = find_folder(ma_ho_so)
    if folder_path:
        os.startfile(folder_path)
        message = "Mở thư mục thành công! đường dẫn: " + folder_path
    else:
        message = "Không tìm thấy thư mục!"

    return render(request, 'myapp/read_xlsx.html', {'message': message})
    