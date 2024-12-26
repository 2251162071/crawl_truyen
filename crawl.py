import subprocess
import os
import json
import shutil

def update_line_numbers(input_data):
    """Cập nhật số dòng cho dữ liệu nhập vào."""
    lines = input_data.strip().split("\n")
    line_numbers = "\n".join(str(i + 1) for i in range(len(lines)))
    return line_numbers

def fetch_links(input_data):
    """Gọi fetch_truyen.sh để tạo file link"""
    lines = input_data.strip().split("\n")
    output_folder = "generated_links"
    os.makedirs(output_folder, exist_ok=True)

    for line in lines:
        try:
            name, chapters = map(str.strip, line.split(":"))
            name = name.strip("'").strip()
            chapters = chapters.strip("'").strip()

            if not name or not chapters.isdigit() or int(chapters) <= 0:
                raise ValueError(f"Invalid input: {line}")

            subprocess.run([
                "bash", "fetch_truyen.sh", name, chapters
            ], check=True)

            output_file = f"{name}_{chapters}.txt"
            if os.path.exists(output_file):
                os.rename(output_file, os.path.join(output_folder, output_file))
        except Exception as e:
            with open("error.log", "a") as error_file:
                error_file.write(f"Error processing line '{line}': {e}\n")

def crawl_data():
    """Gọi run_script.sh để crawl data"""
    output_folder = "generated_links"
    if not os.path.exists(output_folder):
        raise FileNotFoundError("No generated links found! Please generate links first.")

    files = [f for f in os.listdir(output_folder) if f.endswith(".txt")]
    if not files:
        raise FileNotFoundError("No link files found in the generated_links folder!")

    for file_name in files:
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, "r") as file:
            links = file.read().strip().splitlines()

        for link in links:
            try:
                subprocess.run([
                    "bash", "run_script.sh", link
                ], check=True)
            except subprocess.CalledProcessError as e:
                with open("error.log", "a") as error_file:
                    error_file.write(f"Error crawling link '{link}': {e}\n")

def process_json(json_file):
    """Đọc file JSON và tạo file txt với định dạng ten-truyen:số chương, sắp xếp alpha"""
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        output_file = "truyen.txt"
        formatted_data = []

        for entry in data:
            ten_truyen = entry.get("Title_URL", "").split("/")[-2].strip()
            so_chuong = entry.get("Info", "").replace("Chương ", "").strip()

            if ten_truyen and so_chuong.isdigit():
                formatted_data.append(f"{ten_truyen}:{so_chuong}")
            else:
                with open("error.log", "a", encoding="utf-8") as error_file:
                    error_file.write(f"Invalid entry removed: Title_URL={entry.get('Title_URL')} Info={entry.get('Info')}\n")

        formatted_data.sort()

        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write("\n".join(formatted_data))
    except Exception as e:
        raise RuntimeError(f"Lỗi khi xử lý file JSON: {e}")

def extract_chapters():
    """Gọi script extract_chapter.py để xử lý chương."""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extract_chapter.py")
        if not os.path.exists(script_path):
            raise FileNotFoundError("File extract_chapter.py không tồn tại!")

        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Lỗi khi chạy extract_chapter.py: {e}")
    except Exception as e:
        raise RuntimeError(f"Lỗi không xác định: {e}")

def delete_folders_and_files():
    """Xóa thư mục 'generated_links', 'httrack_output' và file 'insert_chapters.sql'."""
    try:
        folders_to_delete = ["generated_links", "httrack_output"]
        file_to_delete = "insert_chapters.sql"

        for folder in folders_to_delete:
            if os.path.exists(folder):
                shutil.rmtree(folder)

        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
    except Exception as e:
        raise RuntimeError(f"Lỗi khi xóa thư mục hoặc file: {e}")

def execute_sql_script():
    """Thực hiện lệnh psql để chạy file insert_chapters.sql."""
    try:
        sql_file = "insert_chapters.sql"
        if not os.path.exists(sql_file):
            raise FileNotFoundError("File insert_chapters.sql không tồn tại!")

        command = [
            "psql",
            "-U", "huandt",
            "-d", "truyenfull",
            "-f", sql_file,
            "--set=ON_ERROR_STOP=off"
        ]
        with open("errors.log", "w") as error_log:
            subprocess.run(command, stderr=error_log, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Lỗi khi thực thi SQL script. Kiểm tra file errors.log để biết thêm chi tiết.")
    except Exception as e:
        raise RuntimeError(f"Lỗi không xác định: {e}")

def execute_all_steps():
    """Thực hiện tất cả các bước: Đọc file, Generate Links, Crawl Data, Extract Chapter, Run SQL Script."""
    try:
        # Đọc nội dung từ thư mục input_data
        input_folder = "input_data"
        if not os.path.exists(input_folder):
            raise FileNotFoundError("Thư mục 'input_data' không tồn tại!")

        input_data = ""
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".txt"):
                file_path = os.path.join(input_folder, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    input_data += file.read() + "\n"

        if not input_data.strip():
            raise ValueError("Không tìm thấy dữ liệu trong các file .txt!")

        # Gọi các bước xử lý
        fetch_links(input_data.strip())
        crawl_data()
        # extract_chapters()
        # execute_sql_script()
    except Exception as e:
        raise RuntimeError(f"Lỗi khi thực hiện các bước: {e}")

delete_folders_and_files()
execute_all_steps()
