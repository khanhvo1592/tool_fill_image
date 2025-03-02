import os
import tkinter as tk
from tkinter import filedialog, messagebox, Scale, Frame, Label
from PIL import Image, ImageTk
import numpy as np
import subprocess
import cv2  # Make sure to install OpenCV with `pip install opencv-python`

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("1000x900")  # Tăng chiều cao để chứa thêm controls
        
        # Mặc định thư mục output
        self.output_directory = os.path.join(os.getcwd(), "output")
        
        # Tạo thư mục output nếu chưa tồn tại
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        
        # Danh sách các file đã chọn
        self.selected_files = []
        
        # Thêm các thông số mới
        self.border_factor = 0.05
        self.blur_strength = 3  # Độ mạnh của blur (1-10)
        self.smoothing_level = 5  # Mức độ làm mịn (1-10)
        self.edge_threshold = 2  # Ngưỡng cạnh (-5 to 5)
        
        # Tạo giao diện
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Convert Images to Black", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Create a horizontal frame to hold controls and preview
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left frame for controls
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Select files button
        select_button = tk.Button(left_frame, text="Select Images", command=self.select_files, width=20, height=2)
        select_button.pack(pady=10)
        
        # Display the number of selected files
        self.file_count_label = tk.Label(left_frame, text="Selected: 0 files")
        self.file_count_label.pack(pady=5)
        
        # Frame for displaying the file list
        list_frame = tk.Frame(left_frame, bd=1, relief=tk.SUNKEN)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)  # Bind selection event
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # Output directory selection
        output_frame = tk.Frame(left_frame)
        output_frame.pack(fill=tk.X, pady=(5, 10))
        
        output_label = tk.Label(output_frame, text="Output directory:")
        output_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.output_path_label = tk.Label(output_frame, text=self.output_directory, bd=1, relief=tk.SUNKEN, anchor="w")
        self.output_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        output_button = tk.Button(output_frame, text="Browse...", command=self.select_output_directory)
        output_button.pack(side=tk.RIGHT)
        
        # Frame cho các điều khiển nâng cao
        advanced_frame = tk.LabelFrame(left_frame, text="Advanced Settings", padx=10, pady=5)
        advanced_frame.pack(fill=tk.X, pady=(10, 5))

        # 1. Border Width
        border_frame = tk.Frame(advanced_frame)
        border_frame.pack(fill=tk.X, pady=2)
        
        border_label = tk.Label(border_frame, text="Border Width:")
        border_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.border_value_label = tk.Label(border_frame, text="5%", width=5)
        self.border_value_label.pack(side=tk.RIGHT)
        
        self.border_slider = Scale(
            border_frame, 
            from_=1, 
            to=20, 
            orient=tk.HORIZONTAL,
            command=self.update_border_value,
            resolution=1,
            length=200
        )
        self.border_slider.set(5)
        self.border_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # 2. Blur Strength
        blur_frame = tk.Frame(advanced_frame)
        blur_frame.pack(fill=tk.X, pady=2)
        
        blur_label = tk.Label(blur_frame, text="Blur Strength:")
        blur_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.blur_value_label = tk.Label(blur_frame, text="3", width=5)
        self.blur_value_label.pack(side=tk.RIGHT)
        
        self.blur_slider = Scale(
            blur_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            command=self.update_blur_value,
            resolution=1,
            length=200
        )
        self.blur_slider.set(3)
        self.blur_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # 3. Smoothing Level
        smooth_frame = tk.Frame(advanced_frame)
        smooth_frame.pack(fill=tk.X, pady=2)
        
        smooth_label = tk.Label(smooth_frame, text="Smoothing:")
        smooth_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.smooth_value_label = tk.Label(smooth_frame, text="5", width=5)
        self.smooth_value_label.pack(side=tk.RIGHT)
        
        self.smooth_slider = Scale(
            smooth_frame,
            from_=1,
            to=10,
            orient=tk.HORIZONTAL,
            command=self.update_smooth_value,
            resolution=1,
            length=200
        )
        self.smooth_slider.set(5)
        self.smooth_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # 4. Edge Threshold
        edge_frame = tk.Frame(advanced_frame)
        edge_frame.pack(fill=tk.X, pady=2)
        
        edge_label = tk.Label(edge_frame, text="Edge Threshold:")
        edge_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edge_value_label = tk.Label(edge_frame, text="2", width=5)
        self.edge_value_label.pack(side=tk.RIGHT)
        
        self.edge_slider = Scale(
            edge_frame,
            from_=-5,
            to=5,
            orient=tk.HORIZONTAL,
            command=self.update_edge_value,
            resolution=1,
            length=200
        )
        self.edge_slider.set(2)
        self.edge_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

        # Thêm nút Preview Settings
        preview_settings_button = tk.Button(advanced_frame, text="Preview Settings", command=self.preview_image)
        preview_settings_button.pack(pady=(5, 0))
        
        # Process images button
        process_button = tk.Button(left_frame, text="Process Images", command=self.process_images, width=20, height=2)
        process_button.pack(pady=(10, 20))  # Add padding to ensure visibility
        
        # Right frame for preview (Explorer-style)
        right_frame = tk.Frame(content_frame, width=300, bd=1, relief=tk.SUNKEN)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        right_frame.pack_propagate(False)  # Prevent the frame from shrinking
        
        # Preview header
        preview_header = tk.Frame(right_frame, bg="#f0f0f0", height=30)
        preview_header.pack(fill=tk.X)
        
        preview_title = tk.Label(preview_header, text="Preview", font=("Arial", 10, "bold"), bg="#f0f0f0")
        preview_title.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Preview button
        preview_button = tk.Button(preview_header, text="Preview", command=self.preview_image)
        preview_button.pack(side=tk.RIGHT, padx=10, pady=2)
        
        # Preview container with padding
        preview_container = tk.Frame(right_frame, padx=10, pady=10)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # Preview image
        self.preview_label = tk.Label(preview_container, text="Select an image to preview")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # File info section
        self.info_frame = tk.Frame(right_frame, bg="#f0f0f0", height=100)
        self.info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # File name
        self.file_name_label = tk.Label(self.info_frame, text="", bg="#f0f0f0", anchor="w")
        self.file_name_label.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # File size
        self.file_size_label = tk.Label(self.info_frame, text="", bg="#f0f0f0", anchor="w")
        self.file_size_label.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        # File dimensions
        self.file_dimensions_label = tk.Label(self.info_frame, text="", bg="#f0f0f0", anchor="w")
        self.file_dimensions_label.pack(fill=tk.X, padx=10, pady=(5, 10))
    
    def update_border_value(self, value):
        percent = int(float(value))
        self.border_value_label.config(text=f"{percent}%")
        self.border_factor = percent / 100
        self.update_preview_if_selected()
    
    def update_blur_value(self, value):
        self.blur_value_label.config(text=str(value))
        self.blur_strength = int(value)
        self.update_preview_if_selected()
        
    def update_smooth_value(self, value):
        self.smooth_value_label.config(text=str(value))
        self.smoothing_level = int(value)
        self.update_preview_if_selected()
        
    def update_edge_value(self, value):
        self.edge_value_label.config(text=str(value))
        self.edge_threshold = int(value)
        self.update_preview_if_selected()

    def update_preview_if_selected(self):
        if self.file_listbox.curselection():
            index = self.file_listbox.curselection()[0]
            file_path = self.selected_files[index]
            self.update_preview(file_path)

    def update_preview(self, file_path):
        try:
            # Process the image
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            
            # Xử lý alpha channel nếu có
            if img.shape[-1] == 4:
                alpha_channel = img[:, :, 3]
                transparent_mask = alpha_channel < 128
                img = img[:, :, :3]
                img[transparent_mask] = [255, 255, 255]
            
            # Lưu lại kích thước gốc
            original_h, original_w = img.shape[:2]
            
            # Tính toán padding
            padding_size = int(max(original_h, original_w) * 0.1)
            
            # Thêm padding
            img_padded = cv2.copyMakeBorder(
                img, 
                padding_size, padding_size, padding_size, padding_size, 
                cv2.BORDER_CONSTANT, 
                value=[255, 255, 255]
            )
            
            # Xử lý ảnh
            img_gray = cv2.cvtColor(img_padded, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(img_gray, 240, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Xử lý ảnh với các thông số hiện tại
            processed_image = self.process_image_with_settings(
                img_padded, 
                img_gray, 
                contours, 
                original_h, 
                original_w, 
                padding_size
            )
            
            # Chuyển đổi sang PIL Image để hiển thị
            pil_img = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
            
            # Tính toán kích thước cho preview
            preview_width = 280
            preview_height = 400
            
            # Tính tỷ lệ để giữ nguyên tỷ lệ khung hình
            width, height = pil_img.size
            ratio = min(preview_width/width, preview_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # Resize ảnh
            pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
            
            # Chuyển đổi sang PhotoImage
            preview_img = ImageTk.PhotoImage(pil_img)
            
            # Cập nhật preview
            self.preview_label.config(image=preview_img)
            self.preview_label.image = preview_img  # Giữ reference
            
        except Exception as e:
            self.preview_label.config(text=f"Could not preview image: {str(e)}")
            self.preview_label.image = None

    def on_file_select(self, event):
        # Get selected index
        if not self.file_listbox.curselection():
            return
        
        index = self.file_listbox.curselection()[0]
        file_path = self.selected_files[index]
        
        # Update preview
        self.update_preview(file_path)
        
        # Update file info
        self.update_file_info(file_path)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Chọn ảnh",
            filetypes=[("Image files", "*.png *.jpg *.jpeg")]
        )
        
        if files:
            self.selected_files = list(files)
            self.file_count_label.config(text=f"Đã chọn: {len(self.selected_files)} file")
            
            # Cập nhật listbox
            self.file_listbox.delete(0, tk.END)
            for file in self.selected_files:
                self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def select_output_directory(self):
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_directory
        )
        
        if directory:
            self.output_directory = directory
            self.output_path_label.config(text=self.output_directory)
            
            # Đảm bảo thư mục tồn tại
            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)
    
    def process_images(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select at least one image!")
            return
        
        processed_count = 0
        
        for file_path in self.selected_files:
            try:
                # Open the image using OpenCV
                img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)  # Đọc cả kênh alpha nếu có
                
                # Xử lý alpha channel nếu có (đổi vùng trong suốt thành trắng)
                if img.shape[-1] == 4:  # Nếu ảnh có kênh alpha (BGRA)
                    # Tách kênh alpha
                    alpha_channel = img[:, :, 3]
                    
                    # Tạo mask cho các vùng trong suốt
                    transparent_mask = alpha_channel < 128  # Ngưỡng alpha để xác định vùng trong suốt
                    
                    # Tạo ảnh RGB (loại bỏ kênh alpha)
                    img = img[:, :, :3]
                    
                    # Đổi vùng trong suốt thành màu trắng
                    img[transparent_mask] = [255, 255, 255]  # BGR format: trắng = [255, 255, 255]
                
                # Lưu lại kích thước gốc của ảnh
                original_h, original_w = img.shape[:2]
                
                # Tính toán kích thước padding dựa trên kích thước ảnh
                padding_size = int(max(original_h, original_w) * 0.1)  # Padding 10% kích thước ảnh
                
                # Thêm padding vào ảnh
                img_padded = cv2.copyMakeBorder(
                    img, 
                    padding_size, padding_size, padding_size, padding_size, 
                    cv2.BORDER_CONSTANT, 
                    value=[255, 255, 255]  # Màu trắng
                )
                
                # Chuyển sang grayscale
                img_gray = cv2.cvtColor(img_padded, cv2.COLOR_BGR2GRAY)
                
                # Find contours of the objects
                contours, _ = cv2.findContours(img_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Thay thế phần xử lý ảnh cũ bằng:
                new_image = self.process_image_with_settings(
                    img_padded, 
                    img_gray, 
                    contours, 
                    original_h, 
                    original_w, 
                    padding_size
                )
                
                # Save the image
                filename = os.path.basename(file_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join(self.output_directory, f"{name}_processed.png")
                
                cv2.imwrite(output_path, new_image)
                processed_count += 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not process file {os.path.basename(file_path)}: {str(e)}")
        
        if processed_count > 0:
            messagebox.showinfo("Success", f"Processed {processed_count} images and saved to '{self.output_directory}'")
            
            # Open the output directory
            output_path = os.path.abspath(self.output_directory)
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.run(['open', output_path])  # macOS
                # subprocess.run(['xdg-open', output_path])  # Linux (uncomment if needed)

    def preview_image(self):
        if not self.selected_files or self.file_listbox.curselection() == ():
            messagebox.showwarning("Warning", "Please select an image from the list!")
            return
        
        index = self.file_listbox.curselection()[0]
        file_path = self.selected_files[index]
        
        try:
            # Process the image
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)  # Đọc cả kênh alpha nếu có
            
            # Xử lý alpha channel nếu có (đổi vùng trong suốt thành trắng)
            if img.shape[-1] == 4:  # Nếu ảnh có kênh alpha (BGRA)
                # Tách kênh alpha
                alpha_channel = img[:, :, 3]
                
                # Tạo mask cho các vùng trong suốt
                transparent_mask = alpha_channel < 128  # Ngưỡng alpha để xác định vùng trong suốt
                
                # Tạo ảnh RGB (loại bỏ kênh alpha)
                img = img[:, :, :3]
                
                # Đổi vùng trong suốt thành màu trắng
                img[transparent_mask] = [255, 255, 255]  # BGR format: trắng = [255, 255, 255]
            
            # Lưu lại kích thước gốc của ảnh
            original_h, original_w = img.shape[:2]
            
            # Tính toán kích thước padding dựa trên kích thước ảnh
            padding_size = int(max(original_h, original_w) * 0.1)  # Padding 10% kích thước ảnh
            
            # Thêm padding vào ảnh
            img_padded = cv2.copyMakeBorder(
                img, 
                padding_size, padding_size, padding_size, padding_size, 
                cv2.BORDER_CONSTANT, 
                value=[255, 255, 255]  # Màu trắng
            )
            
            img_gray = cv2.cvtColor(img_padded, cv2.COLOR_BGR2GRAY)
            _, binary = cv2.threshold(img_gray, 240, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Thay thế phần xử lý ảnh cũ bằng:
            new_image = self.process_image_with_settings(
                img_padded, 
                img_gray, 
                contours, 
                original_h, 
                original_w, 
                padding_size
            )
            
            # Convert to PIL format for display
            pil_img = Image.fromarray(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
            
            # Create a preview window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Processed Preview")
            preview_window.geometry("400x500")
            
            # Calculate the appropriate size for the preview
            max_width = 380
            max_height = 480
            
            # Resize while maintaining aspect ratio
            width, height = pil_img.size
            ratio = min(max_width/width, max_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            pil_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            
            # Display the processed image
            preview_label = tk.Label(preview_window, image=tk_img)
            preview_label.image = tk_img  # Keep a reference
            preview_label.pack(padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not preview image: {str(e)}")

    def update_file_info(self, file_path):
        try:
            # Get file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Convert size to readable format
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Get image dimensions
            img = Image.open(file_path)
            width, height = img.size
            
            # Update labels
            self.file_name_label.config(text=f"File: {file_name}")
            self.file_size_label.config(text=f"Size: {size_str}")
            self.file_dimensions_label.config(text=f"Dimensions: {width} x {height} pixels")
            
        except Exception as e:
            self.file_name_label.config(text=f"File: {os.path.basename(file_path)}")
            self.file_size_label.config(text="Size: Unknown")
            self.file_dimensions_label.config(text="Dimensions: Unknown")

    def process_image_with_settings(self, img_padded, img_gray, contours, original_h, original_w, padding_size):
        # Tính toán kernel size dựa trên border_factor
        min_dim = min(original_h, original_w)
        border_size = int(min_dim * self.border_factor)
        border_size = max(1, border_size)
        
        # 1. Áp dụng threshold để tách đối tượng
        _, binary = cv2.threshold(img_gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # 2. Tạo kernel cho morphological operations
        kernel_size = border_size * 2 + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        # 3. Áp dụng dilate để tạo viền
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # 4. Áp dụng median blur để giảm nhiễu
        median_size = min(self.blur_strength * 2 + 1, 5)
        if median_size % 2 == 0:
            median_size += 1
        smoothed = cv2.medianBlur(dilated, median_size)
        
        # 5. Áp dụng gaussian blur để làm mịn
        blur_size = min(self.smoothing_level * 2 + 1, 9)
        if blur_size % 2 == 0:
            blur_size += 1
        smoothed = cv2.GaussianBlur(smoothed, (blur_size, blur_size), 0)
        
        # 6. Áp dụng threshold cuối cùng
        threshold_value = 128 + (self.edge_threshold * 5)
        _, final_mask = cv2.threshold(smoothed, threshold_value, 255, cv2.THRESH_BINARY)
        
        # 7. Tạo ảnh mới với nền trắng
        new_image = np.ones_like(img_padded) * 255
        
        # 8. Áp dụng mask vào ảnh mới
        new_image[final_mask > 0] = [0, 0, 0]
        
        # 9. Cắt bỏ padding
        new_image = new_image[padding_size:padding_size+original_h, padding_size:padding_size+original_w]
        
        return new_image

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop() 