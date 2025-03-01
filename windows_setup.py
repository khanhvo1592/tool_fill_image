import PyInstaller.__main__
import os

# Đường dẫn đến icon (nếu có)
icon_path = 'app_icon.ico'  # Thay đổi thành đường dẫn đến file icon của bạn nếu có

# Kiểm tra xem file icon có tồn tại không
icon_option = []
if os.path.exists(icon_path):
    icon_option = ['--icon', icon_path]

PyInstaller.__main__.run([
    'image_processor.py',
    '--name=Image Processor',
    '--windowed',  # Tạo ứng dụng GUI không hiển thị console
    '--onefile',   # Đóng gói tất cả vào một file .exe
    '--add-data=output;output',  # Thêm thư mục output vào gói
    '--clean',     # Xóa các file tạm trước khi build
    *icon_option,  # Thêm icon nếu có
])

print("Build completed. The executable is in the 'dist' folder.") 