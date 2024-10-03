# Sử dụng image Python chính thức
FROM python:3.12-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt vào image
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào image
COPY . .
# Thực hiện migrations (nên thực hiện sau khi sao chép mã nguồn)
RUN python manage.py makemigrations && \
    python manage.py migrate

# Reset db (nên chạy sau khi đã thực hiện migrations)
RUN python manage.py flush --no-input
# Chạy lệnh để khởi động server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
