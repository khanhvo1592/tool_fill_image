from setuptools import setup

APP = ['image_processor.py']  # Tên file chính của ứng dụng
DATA_FILES = []  # Nếu có file dữ liệu nào cần bao gồm, thêm vào đây
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PIL', 'numpy', 'cv2'],
    'includes': ['jaraco.text', 'pkg_resources'],  # Thêm các module cần thiết
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)