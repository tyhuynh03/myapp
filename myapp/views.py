import csv
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from .models import Product
import os
from django.core.paginator import Paginator

############################################################################################
column_keywords = {
    'ARTICLE': ['Article'],
    'NAME': ['Name','Description','Article Description'],
    'BARCODE': ['Barcode No.','Barcode','barcode'],
    'date_creat': ['Date creat','Ngày tạo','date creat'],
    'VENDOR': ['Vendor'],
    'Ngày hết hiệu lực': ['Ngày hết hiệu lực','Ngày hết hiệu lực\n(Tháng/ngày/năm)'],
    'Mã hồ sơ': ['Mã hồ sơ','Mã số hồ sơ','Mã số hồ sơ.1','Mã hồ sơ.1',],
}
# Danh sách các cột bắt buộc trong model
required_columns = list(column_keywords.keys())
# Hàm lọc cột không cần thiết
def filter_columns(df, required_columns):
    valid_columns = [col for col in required_columns if col in df.columns]
    return df[valid_columns]
# Hàm ánh xạ tên cột
def map_columns(df, column_keywords):
    # Tạo từ điển ánh xạ từ các từ khóa về tên chuẩn hóa
    mapping = {}
    for standard_col, keywords in column_keywords.items():
        for keyword in keywords:
            if keyword in df.columns:
                mapping[keyword] = standard_col
    # Đổi tên cột dựa trên ánh xạ
    df = df.rename(columns=mapping)
    return df
def rename_duplicate_columns(columns):
    seen = {}
    new_columns = []
    for col in columns:
        if col in seen:
            seen[col] += 1
            new_columns.append(f"{col}.{seen[col]}")
        else:
            seen[col] = 0
            new_columns.append(col)
    return new_columns
##########################################################################################
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
        
        # Ánh xạ tên cột
        df = map_columns(df, column_keywords)
        # Lọc cột không cần thiết
        df = filter_columns(df, required_columns)
        df.columns = rename_duplicate_columns(df.columns)
        if 'Mã hồ sơ' in df.columns and 'Mã hồ sơ.1' in df.columns:
            df = df.drop(columns=['Mã hồ sơ'])
            df = map_columns(df, column_keywords)

        # Xử lý cột ARTICLE để loại bỏ phần '.0'
        df['ARTICLE'] = df['ARTICLE'].astype(str).str.replace('.0', '', regex=False)
        data = df.to_dict(orient='records')
        #Lưu dữ liệu vào model
        for item in data:
            try:
                product, created = Product.objects.get_or_create(
                    article=item['ARTICLE'],
                    defaults={
                        'name': item['NAME'],
                        'barcode': item['BARCODE'],
                        'date_created': item['date_creat'],
                        'Vendor': item['VENDOR'],
                        'ngay_het_hieu_luc': item['Ngày hết hiệu lực'],
                        'ma_ho_so': item['Mã hồ sơ'],
                    }
                )
                if created:
                    print(f"Đã thêm mới sản phẩm {item['ARTICLE']}")
                else:
                    print(f"Sản phẩm {item['ARTICLE']} đã tồn tại.")
            except ValidationError as e:
                print(f"Lỗi khi thêm sản phẩm {item['ARTICLE']}: {e}")
        print("Đọc file XLSX thành công!")

    return redirect('home')

def home(request):
    products = Product.objects.all()  # Lấy tất cả các sản phẩm
    paginator = Paginator(products, 100)  # Mỗi trang có 100 sản phẩm
    page_number = request.GET.get('page')  # Lấy số trang từ query parameter
    page_obj = paginator.get_page(page_number)  # Lấy đối tượng phân trang cho trang hiện tại
    return render(request, 'myapp/home.html', {'page_obj': page_obj})  # Truyền page_obj vào template



######################################################################################################################
def search(request):
    if request.method == 'POST':
        search = request.POST['search']
        print(search)
        products = Product.objects.filter(article__icontains=search)
        return render(request, 'myapp/home.html', {'page_obj': products})
    return render(request, 'myapp/home.html')

# def find_folder(folder_name, search_path='/app/mydrive'):
#     for drive in os.walk(search_path):
#         for root, dirs, files in os.walk(drive + "\\"):
#             if folder_name in dirs:
#                 return os.path.join(root, folder_name)
#     return None
import os
import time
# Bản đồ mã thư mục với tên thư mục
FOLDER_MAP = {
    "11": "11-105 Tươi sống",
    "12": "12-102 Hàng Mát",
    "13": "13-101 Đông lạnh",
    "14": "14-103 Bánh mì",
    "15": "15-103 Chế Biến",
    "21": "21-104 Thực phẩm khô",
    "22": "22-106 Đồ Uống, thuốc lá",
    "23": "23-106 Bánh kẹo"
}
def find_folder(folder_name, base_dirs=[r'\\masan.local\12. An Ninh Va Thanh Tra\99.12.1 Ho So Chat Luong\99.12.1.2PCU\\1. Hồ sơ chất lượng_Thực phẩm']):
    """
    Tìm thư mục theo tên file, chỉ giới hạn tìm trong thư mục được xác định từ mã đầu của tên file.
    """
    # Xác định mã thư mục từ phần đầu của tên file
    main_code = folder_name.split('.')[0][:2]
    main_folder = FOLDER_MAP.get(main_code)  # Lấy tên thư mục chính dựa trên mã đầu tiên
    
    if main_folder is None:
        return "Mã không hợp lệ hoặc không có trong danh sách thư mục"
    
    # Xây dựng đường dẫn thư mục chính xác để tìm kiếm
    search_path = os.path.join(base_dirs[0], main_folder)
    
    # Kiểm tra nếu đường dẫn tồn tại
    if not os.path.exists(search_path):
        return "Thư mục chính xác không tồn tại!"

    # Tìm kiếm trong thư mục cụ thể
    for root, dirs, files in os.walk(search_path, topdown=True):
        # Giới hạn chiều sâu tìm kiếm
        if root.count(os.sep) - search_path.count(os.sep) > 3:
            dirs.clear()  # Dừng duyệt các thư mục con sâu hơn
        if folder_name in dirs:
            return os.path.join(root, folder_name)

    return None





def open_folder(request,ma_ho_so):
    # Bắt đầu đo thời gian tìm kiếm
    start_time = time.time()
    
    # Đầu tiên thử tìm thư mục với tên đầy đủ
    prefix_name = '.'.join(ma_ho_so.split('.')[:2])
    folder_path = find_folder(prefix_name)
    
    # Nếu không tìm thấy, thử tìm với tên ngắn hơn
    # if not folder_path:
    #     prefix_name = '.'.join(ma_ho_so.split('.')[:2])  # Lấy 2 phần đầu của tên (ví dụ 23.220040)
    #     folder_path = find_folder(prefix_name)
    
    # Kết thúc đo thời gian tìm kiếm
    search_time = time.time() - start_time
    # Kiểm tra kết quả và mở thư mục nếu tìm thấy
    if folder_path:
        os.startfile(folder_path)
        message = f"Mở thư mục thành công! Đường dẫn: {folder_path}. Thời gian tìm kiếm: {search_time:.4f} giây."
    else:
        message = f"Không tìm thấy thư mục! Thời gian tìm kiếm: {search_time:.4f} giây."
    return render(request, 'myapp/read_xlsx.html', {'message': message})