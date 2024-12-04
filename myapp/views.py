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
    'ARTICLE': ['Article','Article','No SAP','Mã hàng hóa','tên','Article '],
    'NAME': ['Name','Description','Article Description','Article Description','Tên hàng hóa'],
    'BARCODE': ['Barcode No.','Barcode','barcode'],
    'date_creat': ['Date creat','Ngày tạo','date creat','Số CN hồ sơ','STT'],
    'VENDOR': ['Vendor','Vendor SAP','Mã NCC','SAP Vendor No.'],
    'Vendor name': ['Tên NCC','Tên NCC'],
    'Ngày hết hiệu lực': ['Ngày hết hiệu lực','Ngày hết hiệu lực\n(Tháng/ngày/năm)','Ngày hết hiệu lực','Ngày HHL','Tình trạng hiệu lực','Số CB/ Số TCCS'],
    'Mã hồ sơ': ['Mã hồ sơ','Mã số hồ sơ','Mã số hồ sơ.1','Mã hồ sơ.1','Mã hồ sơ ','Mã hóa hồ sơ lưu'],
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
                        'Vendor_name' : item['Vendor name'],
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
    # Thực phẩm
    "11": "11-105 Tươi sống",
    "12": "12-102 Hàng Mát",
    "13": "13-101 Đông lạnh",
    "14": "14-103 Bánh mỳ",
    "15": "15-103 Chế Biến",
    "21": "21-104 Thực phẩm khô",
    "22": "22-106 Đồ Uống, thuốc lá",
    "23": "23-106 Bánh kẹo",
    # Phi thực phẩm 
    "24": "24 - Mỹ phẩm chăm sóc cá nhân",
    "25": "25 - Hóa phẩm",
    "26": "26 - Dệt may",
    "41": "41 - Gia dụng",
    "42": "42 - Điện gia dụng",
    "43": "43 - Mũ bảo hiểm",
    "45": "45 - Đồ chơi",
    "46": "46 - Đèn led huỳnh quang các loại",
    "47": "47 - Giải trí thể thao",
    "50": "50 - VAT TU TIEU HAO",


}
# def find_folder(folder_name, base_dirs=[r'D:\\']):
def find_folder(folder_name, base_dirs=[r'\\masan.local\12. An Ninh Va Thanh Tra\99.12.1 Ho So Chat Luong\99.12.1.2PCU']):
    """
    Tìm thư mục theo tên, giới hạn trong loại thư mục Thực phẩm hoặc Phi thực phẩm.
    
    Args:
        folder_name (str): Tên thư mục cần tìm.
        base_dirs (list): Danh sách đường dẫn cơ sở để tìm kiếm.
    
    Returns:
        str: Đường dẫn thư mục nếu tìm thấy, hoặc thông báo lỗi nếu không tìm thấy.
    """
    if not folder_name:
        return "Tên thư mục không được để trống."
    
    # Lấy mã thư mục từ tên
    main_code = folder_name.split('.')[0][:2]
    main_folder = FOLDER_MAP.get(main_code)
    
    if main_folder is None:
        return "Mã không hợp lệ hoặc không có trong danh sách thư mục."
    
    # Xác định đường dẫn cơ sở phù hợp
    if main_code in ["11", "12", "13", "14", "15", "21", "22", "23"]:  # Thực phẩm
        adjusted_base_dir = os.path.join(base_dirs[0], "1. Hồ sơ chất lượng_Thực phẩm")
    elif main_code in ["24", "25", "26", "41", "42", "43", "45", "46", "47", "50"]:  # Phi thực phẩm
        adjusted_base_dir = os.path.join(base_dirs[0], "2. Hồ sơ chất lượng_Phi thực phẩm")
    else:
        return "Mã thư mục không thuộc Thực phẩm hoặc Phi thực phẩm."
    
    # Xây dựng đường dẫn chính xác để tìm kiếm
    search_path = os.path.join(adjusted_base_dir, main_folder)
    if not os.path.exists(search_path):
        return f"Thư mục không tồn tại: {search_path}"
    

    # Tìm kiếm trong thư mục cụ thể
    for root, dirs, files in os.walk(search_path, topdown=True):
        # Giới hạn chiều sâu tìm kiếm
        if root.count(os.sep) - search_path.count(os.sep) > 3:
            dirs.clear()  # Dừng duyệt các thư mục con sâu hơn
        if folder_name in dirs:
            return os.path.join(root, folder_name)

    return None


def find_folder_in_subfolder(parent_folder, subfolder_name):
    """
    Tìm thư mục con trong một thư mục cấp trên
    """
    for root, dirs, files in os.walk(parent_folder):
        if subfolder_name in dirs:
            return os.path.join(root, subfolder_name)
    return None


def open_folder(request,ma_ho_so):
    article = request.GET.get('article')
    products = Product.objects.filter(article__icontains=article)
    # Bắt đầu đo thời gian tìm kiếm
    start_time = time.time()                                    
    # Đầu tiên thử tìm thư mục với tên đầy đủ
    prefix_name = '.'.join(ma_ho_so.split('.')[:2])
    
    folder_path = find_folder(prefix_name)
    # nếu tìm thấy thư mục cấp 2 thì tìm tiếp trong thư mục cấp 2
    if folder_path:
        folder_full_name = ma_ho_so        
        folder_path_v1 = find_folder_in_subfolder(folder_path, folder_full_name)
    # Kết thúc đo thời gian tìm kiếm
    search_time = time.time() - start_time
    # Kiểm tra kết quả và mở thư mục nếu tìm thấy
    if folder_path_v1:
        os.startfile(folder_path_v1)
        message = f"Mở thư mục thành công! Đường dẫn: {folder_path_v1}. Thời gian tìm kiếm: {search_time:.4f} giây."
        return render(request, 'myapp/home.html', {'page_obj': products, 'message': message})
    if folder_path:
        os.startfile(folder_path)
        message = f"Mở thư mục thành công! Đường dẫn: {folder_path_v1}. Thời gian tìm kiếm: {search_time:.4f} giây."
    else:
        message = f"Không tìm thấy thư mục! Thời gian tìm kiếm: {search_time:.4f} giây."
    return render(request, 'myapp/home.html', {'page_obj': products, 'message': message})


### function find folder by vendor 
from django.shortcuts import render
import re 
from unidecode import unidecode
BASE_DIR = r'\\masan.local\12. An Ninh Va Thanh Tra\99.12.1 Ho So Chat Luong\99.12.1.2PCU\1. Hồ sơ chất lượng_Thực phẩm\GIẤY CHỨNG NHẬN ATTP-NCC'
def find_folder_by_vendor(request):
    found = False
    if request.method == "POST":
        vendor = request.POST.get('vendor')  # Lấy giá trị từ input có name="vendor"
        # bỏ khoảng trắng ở đầu và cuối chuỗi
        vendor = vendor.strip()
    # Chuẩn hóa chuỗi nhập từ người dùng
    vendor_normalized = unidecode(vendor.strip().lower())

    # Kiểm tra thư mục gốc có tồn tại
    if os.path.exists(BASE_DIR):
        for folder in os.listdir(BASE_DIR):
            folder_path = os.path.join(BASE_DIR, folder)
            if os.path.isdir(folder_path):  # Chỉ kiểm tra thư mục
                # Chuẩn hóa tên thư mục
                folder_normalized = unidecode(folder.strip().lower())

                # Sử dụng `re.search` để tìm từ khóa trong tên thư mục
                if re.search(re.escape(vendor_normalized), folder_normalized):
                    print(f"Thư mục đã tìm thấy: {folder_path} ")
                    os.startfile(folder_path)
                    found = True
    if not False:
        print('Không tìm thấy thư mục')
    

    return render(request, 'myapp/home.html' )

# def support_find_folder_by_venfor(vendor_code, vendor_name,base_dir=[]):
#     try:
#         for folder in os.listdir(base_dir[0]):
#             folder_path = os.path.join(base_dir[0], folder)
#             number = re.findall(r'\d+', folder)
#             print(number)
#             if '11' in number:
#                 print('thư mục chứa 11')
#                 if os.path.isdir(folder_path) and vendor_name in folder:
#                     return folder_path
#             else:
#                 if os.path.isdir(folder_path) and vendor_code in folder:
#                     return folder_path
#     except FileNotFoundError as e:
#         return f"Không tìm thấy thư mục: {base_dir[0]}"
#     except PermissionError:
#         return f"Không có quyền truy cập thư mục: {base_dir[0]}"
#     return f"Không tìm thấy thư mục cho nhà cung cấp: {vendor_name} - {vendor_code}"