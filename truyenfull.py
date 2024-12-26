import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json

class ToolTip:
    def __init__(self, widget, text="widget info"):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Hiển thị tooltip khi mouse pointer đi vào widget."""
        if self.tip_window or not self.text:
            return
        # Tạo cửa sổ Toplevel để hiển thị tooltip
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # bỏ viền cửa sổ

        # Tính toán vị trí hiển thị tooltip
        x = event.x_root + 10
        y = event.y_root + 10
        tw.wm_geometry(f"+{x}+{y}")

        # Tạo một Label để hiển thị nội dung tooltip
        label = tk.Label(tw, text=self.text, background="yellow",
                         fg="black", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1, ipady=1)

    def hide_tooltip(self, event=None):
        """Ẩn tooltip khi mouse pointer rời khỏi widget."""
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None


def update_line_numbers(*args):
    """Cập nhật số dòng cho widget line_numbers."""
    line_numbers.config(state=tk.NORMAL)
    line_numbers.delete("1.0", tk.END)
    lines = text_input.get("1.0", tk.END).split("\n")
    for i in range(1, len(lines) + 1):
        line_numbers.insert(tk.END, f"{i}\n")
    line_numbers.config(state=tk.DISABLED)

def fetch_links():
    """Gọi fetch_truyen.sh để tạo file link"""
    input_data = text_input.get("1.0", tk.END).strip()
    lines = input_data.split("\n")
    output_folder = "generated_links"
    os.makedirs(output_folder, exist_ok=True)
    
    for line in lines:
        try:
            # Parse input
            name, chapters = map(str.strip, line.split(":"))
            name = name.strip("'").strip()
            chapters = chapters.strip("'").strip()
            
            # Validate input
            if not name or not chapters.isdigit() or int(chapters) <= 0:
                raise ValueError(f"Invalid input: {line}")
            
            # Run fetch_truyen.sh
            subprocess.run(
                ["bash", "fetch_truyen.sh", name, chapters],
                check=True
            )
            
            # Move the generated file to the output folder
            output_file = f"{name}_{chapters}.txt"
            if os.path.exists(output_file):
                os.rename(output_file, os.path.join(output_folder, output_file))
        except Exception as e:
            with open("error.log", "a") as error_file:
                error_file.write(f"Error processing line '{line}': {e}\n")
    
    # messagebox.showinfo("Done", "Links have been generated!")

def crawl_data():
    """Gọi run_script.sh để crawl data"""
    output_folder = "generated_links"
    if not os.path.exists(output_folder):
        messagebox.showerror("Error", "No generated links found! Please generate links first.")
        return

    # Get list of files in the output folder
    files = [f for f in os.listdir(output_folder) if f.endswith(".txt")]
    if not files:
        messagebox.showerror("Error", "No link files found in the generated_links folder!")
        return

    progress["maximum"] = len(files)
    progress["value"] = 0

    # Process each file
    for file_index, file_name in enumerate(files, start=1):
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, "r") as file:
            links = file.read().strip().splitlines()
        
        for link in links:
            try:
                subprocess.run(
                    ["bash", "run_script.sh", link],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                with open("error.log", "a") as error_file:
                    error_file.write(f"Error crawling link '{link}': {e}\n")

        # Update progress bar
        progress["value"] = file_index
        root.update_idletasks()
    
    # messagebox.showinfo("Done", "Data has been crawled!")

def load_file():
    """Đọc dữ liệu từ nhiều file nhập"""
    file_paths = filedialog.askopenfilenames(
        title="Select Input Files",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_paths:
        for file_path in file_paths:
            with open(file_path, "r") as file:
                content = file.read()
            text_input.insert(tk.END, content.strip() + "\n")
    update_line_numbers()

def load_json():
    """Đọc file JSON và xử lý"""
    json_file = filedialog.askopenfilename(
        title="Select JSON File",
        filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
    )
    if json_file:
        process_json(json_file)
        update_line_numbers()

def process_json(json_file):
    """Đọc file JSON và tạo file txt với định dạng ten-truyen:số chương, sắp xếp alpha"""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        output_file = "truyen.txt"
        formatted_data = []

        # Trích xuất dữ liệu từ JSON và định dạng
        for entry in data:
            ten_truyen = entry.get("Title_URL", "").split("/")[-2].strip()  # Tách ten-truyen từ Title_URL
            so_chuong = entry.get("Info", "").replace("Chương ", "").strip()  # Tách số chương từ Info

            # Kiểm tra tính hợp lệ
            if ten_truyen and so_chuong.isdigit():  # Chỉ chấp nhận nếu so_chuong là số nguyên
                formatted_data.append(f"{ten_truyen}:{so_chuong}")
            else:
                # Ghi log nếu dữ liệu không hợp lệ
                with open("error.log", "a", encoding="utf-8") as error_file:
                    error_file.write(f"Invalid entry removed: Title_URL={entry.get('Title_URL')} Info={entry.get('Info')}\n")

        # Sắp xếp danh sách theo thứ tự alpha
        formatted_data.sort()

        # Ghi ra file
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write("\n".join(formatted_data))
        
        # messagebox.showinfo("Success", f"File {output_file} đã được tạo thành công, sắp xếp alpha!")
    except Exception as e:
        messagebox.showerror("Error", f"Lỗi khi xử lý file JSON: {e}")

def extract_chapters():
    """Gọi script extract_chapter.py để xử lý chương."""
    try:
        # Đảm bảo file extract_chapter.py nằm cùng thư mục
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_chapter.py")
        if not os.path.exists(script_path):
            messagebox.showerror("Error", "File extract_chapter.py không tồn tại!")
            return
        
        # Chạy script
        subprocess.run(["python", script_path], check=True)
        # messagebox.showinfo("Success", "Extract chapters thành công!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Lỗi khi chạy extract_chapter.py: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Lỗi không xác định: {e}")

import shutil

def delete_folders_and_files():
    """Xóa thư mục 'generated_links', 'httrack_output' và file 'insert_chapters.sql'."""
    try:
        folders_to_delete = ["generated_links", "httrack_output"]
        file_to_delete = "insert_chapters.sql"
        
        # Xóa thư mục
        for folder in folders_to_delete:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"Deleted folder: {folder}")
        
        # Xóa file
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
            print(f"Deleted file: {file_to_delete}")
        
        # messagebox.showinfo("Success", "Deleted specified folders and files successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Lỗi khi xóa thư mục hoặc file: {e}")

def execute_sql_script():
    """Thực hiện lệnh psql để chạy file insert_chapters.sql."""
    try:
        # Kiểm tra xem file insert_chapters.sql có tồn tại không
        sql_file = "insert_chapters.sql"
        if not os.path.exists(sql_file):
            messagebox.showerror("Error", "File insert_chapters.sql không tồn tại!")
            return

        # Thực hiện lệnh psql
        command = [
            "psql",
            "-U", "huandt",
            "-d", "truyenfull",
            "-f", sql_file,
            "--set=ON_ERROR_STOP=off"
        ]
        with open("errors.log", "w") as error_log:
            subprocess.run(command, stderr=error_log, check=True)
        
        # messagebox.showinfo("Success", "SQL script đã được thực thi thành công!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Lỗi khi thực thi SQL script. Kiểm tra file errors.log để biết thêm chi tiết.")
    except Exception as e:
        messagebox.showerror("Error", f"Lỗi không xác định: {e}")

def execute_all_steps():
    """Thực hiện tất cả các bước: Generate Links, Crawl Data, Extract Chapter, Run SQL Script."""
    try:
        # Step 1: Generate Links
        fetch_links()
        # messagebox.showinfo("Step 1", "Generate Links completed.")

        # Step 2: Crawl Data
        crawl_data()
        # messagebox.showinfo("Step 2", "Crawl Data completed.")

        # Step 3: Extract Chapter
        extract_chapters()
        # messagebox.showinfo("Step 3", "Extract Chapter completed.")

        # Step 4: Run SQL Script
        execute_sql_script()
        # messagebox.showinfo("Step 4", "Run SQL Script completed.")

        # Final message
        messagebox.showinfo("Success", "All steps completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Lỗi khi thực hiện các bước: {e}")






# Create GUI
root = tk.Tk()
root.title("Truyen Crawler")
root.geometry("1000x480")

# Input instructions
instructions = tk.Label(root, text="Enter stories and chapter counts (e.g., 'ten-truyen : so-chuong'): ")
instructions.pack(pady=5)

# Create a frame to hold line_numbers and text_input
text_frame = tk.Frame(root)
text_frame.pack(pady=5)

# Line numbers
line_numbers = tk.Text(text_frame, width=4, height=15, bg="lightgrey", fg="black", state=tk.DISABLED)
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

# Text input with vertical scrollbar
text_scrollbar = tk.Scrollbar(text_frame)
text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_input = tk.Text(text_frame, height=15, width=66, yscrollcommand=text_scrollbar.set)
text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

text_scrollbar.config(command=text_input.yview)

# Bind update_line_numbers to events
text_input.bind("<KeyRelease>", update_line_numbers)
text_input.bind("<MouseWheel>", update_line_numbers)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress.pack(pady=10)

# Create a frame to hold buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Nút đọc JSON với màu sắc riêng
json_button = tk.Button(button_frame, text="Read JSON", command=load_json, bg="blue", fg="white")
json_button.pack(side=tk.LEFT, padx=5)

# Tạo tooltip cho nút Read JSON
ToolTip(json_button, text="1. Nhấn để chọn và đọc file JSON.\nTự động trích xuất thành 'tên-truyện : số-chương'.")

# Load file button với màu sắc riêng
load_button = tk.Button(button_frame, text="Load File", command=load_file, bg="green", fg="white")
load_button.pack(side=tk.LEFT, padx=5)

# Tạo tooltip cho nút Load File
ToolTip(load_button, text="2. Nhấn để  load file txt.\nMỗi dòng chứa 'tên-truyện : số-chương'.")

# Fetch links button với màu sắc riêng
fetch_button = tk.Button(button_frame, text="Generate Links", command=fetch_links, bg="orange", fg="black")
fetch_button.pack(side=tk.LEFT, padx=5)

# Tạo tooltip cho nút Fetch Links
ToolTip(fetch_button, text="3. Nhấn để tạo file link từ 'tên-truyện : số-chương'.")

# Crawl data button với màu sắc riêng
crawl_button = tk.Button(button_frame, text="Crawl Data", command=crawl_data, bg="red", fg="white")
crawl_button.pack(side=tk.LEFT, padx=5)

# Extract Chapter button với tooltip
extract_button = tk.Button(button_frame, text="Extract Chapter", command=extract_chapters, bg="purple", fg="white")
extract_button.pack(side=tk.LEFT, padx=5)

# Run SQL Script button với tooltip
run_sql_button = tk.Button(button_frame, text="Run SQL Script", command=execute_sql_script, bg="darkblue", fg="white")
run_sql_button.pack(side=tk.LEFT, padx=5)

# Tạo tooltip cho nút Run SQL Script
ToolTip(run_sql_button, text="6. Nhấn để thực thi lệnh SQL từ file insert_chapters.sql vào PostgreSQL.")


# Delete Folders and Files button với tooltip
delete_button = tk.Button(button_frame, text="Delete Folders & Files", command=delete_folders_and_files, bg="brown", fg="white")
delete_button.pack(side=tk.LEFT, padx=5)

# Tạo tooltip cho nút Delete Folders & Files
ToolTip(delete_button, text="7. Nhấn để xóa thư mục 'generated_links', 'httrack_output' và file 'insert_chapters.sql'.")

# Execute All Steps button với tooltip
execute_all_button = tk.Button(button_frame, text="Execute All Steps", command=execute_all_steps, bg="darkgreen", fg="white")
execute_all_button.pack(side=tk.LEFT, padx=5)

# Tạo tooltip cho nút Execute All Steps
# ToolTip(execute_all_button, text="8. Nhấn để thực hiện tất cả các bước: Generate Links, Crawl Data, Extract Chapter, Run SQL Script.")

# Tạo tooltip cho nút Extract Chapter
# ToolTip(extract_button, text="5. Nhấn để extract dữ liệu từ index.html và lưu vào SQL script.")


# Tạo tooltip cho nút Crawl Data
# ToolTip(crawl_button, text="4. Nhấn để crawl dữ liệu từ các file link đã tạo.")

# Initialize line numbers
update_line_numbers()

# Run the application
root.mainloop()
