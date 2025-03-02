import PyInstaller.__main__
import os

# Tạo thư mục output nếu chưa tồn tại
if not os.path.exists('output'):
    os.makedirs('output')

PyInstaller.__main__.run([
    'image_processor.py',
    '--name=Image Processor',
    '--windowed',  # Tạo ứng dụng GUI không hiển thị console
    '--onefile',   # Đóng gói tất cả vào một file .exe
    '--add-data=output;output',  # Thêm thư mục output vào gói
    '--clean',     # Xóa các file tạm trước khi build
])

print("Build completed. The executable is in the 'dist' folder.") 