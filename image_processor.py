import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import subprocess
import cv2  # Make sure to install OpenCV with `pip install opencv-python`

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor")
        self.root.geometry("600x400")
        
        # Tạo thư mục output nếu chưa tồn tại
        if not os.path.exists("output"):
            os.makedirs("output")
        
        # Danh sách các file đã chọn
        self.selected_files = []
        
        # Tạo giao diện
        self.create_widgets()
    
    def create_widgets(self):
        # Frame chính
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = tk.Label(main_frame, text="Chuyển đổi ảnh sang màu đen-trắng", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Nút chọn file
        select_button = tk.Button(main_frame, text="Chọn ảnh", command=self.select_files, width=20, height=2)
        select_button.pack(pady=10)
        
        # Hiển thị số lượng file đã chọn
        self.file_count_label = tk.Label(main_frame, text="Đã chọn: 0 file")
        self.file_count_label.pack(pady=5)
        
        # Khung hiển thị danh sách file
        list_frame = tk.Frame(main_frame, bd=1, relief=tk.SUNKEN)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.file_listbox.yview)
        
        # Nút xử lý ảnh
        process_button = tk.Button(main_frame, text="Xử lý ảnh", command=self.process_images, width=20, height=2)
        process_button.pack(pady=10)
    
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
    
    def process_images(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select at least one image!")
            return
        
        processed_count = 0
        
        for file_path in self.selected_files:
            try:
                # Open the image using OpenCV
                img = cv2.imread(file_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
                
                # Apply a binary threshold to get a binary image
                _, binary = cv2.threshold(img_gray, 240, 255, cv2.THRESH_BINARY_INV)  # Invert the colors
                
                # Find contours of the objects
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Create a new image with the same dimensions as the original
                new_image = np.ones_like(img) * 255  # Start with a white background
                
                # Fill the contours with black
                cv2.drawContours(new_image, contours, -1, (0, 0, 0), thickness=cv2.FILLED)
                
                # Save the image
                filename = os.path.basename(file_path)
                name, _ = os.path.splitext(filename)
                output_path = os.path.join("output", f"{name}_processed.png")
                
                cv2.imwrite(output_path, new_image)
                processed_count += 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not process file {os.path.basename(file_path)}: {str(e)}")
        
        if processed_count > 0:
            messagebox.showinfo("Success", f"Processed {processed_count} images and saved to 'output'")
            
            # Open the output directory
            output_path = os.path.abspath("output")
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.run(['open', output_path])  # macOS
                # subprocess.run(['xdg-open', output_path])  # Linux (uncomment if needed)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop() 