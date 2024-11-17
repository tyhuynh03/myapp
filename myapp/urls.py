from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Đường dẫn chính
    path('upload-xlsx/', views.upload_xlsx, name='upload_xlsx'),  # Đường dẫn upload file
    path('search/', views.search, name='search'),  # Đường dẫn tìm kiếm
    path('open-folder/<str:ma_ho_so>/', views.open_folder, name='open_folder'),  # Đường dẫn mở thư mục
]
