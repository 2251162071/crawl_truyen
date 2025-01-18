import subprocess
import psycopg2
import logging
import os, re, sys
import subprocess
from bs4 import BeautifulSoup
import requests

# Cấu hình logging
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CRAWL_URL = "truyenfull.bio"
IS_UPDATE = True   # Cập nhật truyện đã tồn tại

# Hàm kiểm tra sự tồn tại của truyện
def check_story_exists(story_name, cursor):
    print(f"Kiểm tra sự tồn tại của truyện {story_name}")
    query = "SELECT external_id FROM app_truyen_story WHERE title = %s LIMIT 1;"
    cursor.execute(query, (story_name,))
    result = cursor.fetchone()
    print("Debug result:", result)
    return result is not None

# Hàm crawl thông tin truyện
def crawl_story(story_name, total_chapters):
    try:
        url = f"https://{CRAWL_URL}/{story_name}/"

        # Thư mục lưu nội dung tải về
        output_dir = "truyen_info"

        # Bước 1: Tải nội dung từ URL
        crawl_truyen(url, output_dir)

        # Bước 2: Lấy thông tin truyện từ nội dung đã tải
        thong_tin_truyen = extract_truyen_info(output_dir, url)
        print('thong tin truyen ===')

        if thong_tin_truyen:
            # Kết nối cơ sở dữ liệu
            conn = psycopg2.connect(
                dbname="defaultdb",
                host="truyenso-do-user-14364101-0.m.db.ondigitalocean.com",
                port=25060,
                user="doadmin",
            )
            cursor = conn.cursor()

            # Kiểm tra sự tồn tại của truyện
            is_exist = check_story_exists(story_name, cursor)
            print(is_exist)
            print(IS_UPDATE)
            if is_exist and IS_UPDATE:
                # Thực hiện cập nhật nếu IS_UPDATE là True
                query = """
                    UPDATE public.app_truyen_story
                    SET 
                        title_full = %s,
                        author = %s,
                        status = %s,
                        chapter_number = %s,
                        image = %s,
                        image_blob = %s,
                        description = %s,
                        views = %s,
                        rating = %s,
                        so_luot = %s,
                        updated_at = NOW()
                    WHERE title = %s;
                """
                cursor.execute(query, (
                    thong_tin_truyen["ten_truyen_full"],  # title_full
                    thong_tin_truyen["tac_gia"],          # author
                    thong_tin_truyen["trang_thai"],       # status
                    total_chapters,                       # chapter_number
                    thong_tin_truyen["image"],            # image
                    psycopg2.Binary(thong_tin_truyen["image_blob"]),  # image_blob
                    thong_tin_truyen["description_html"], # description
                    0,                                    # views
                    thong_tin_truyen["rating_value"],     # rating
                    thong_tin_truyen["so_luot"],           # so_luot
                    story_name                            # title
                ))
                print(f"Đã cập nhật thông tin truyện: {story_name}")
            elif not is_exist:
                # Thực hiện chèn nếu truyện chưa tồn tại
                query = """
                    INSERT INTO public.app_truyen_story 
                    (title, title_full, author, status, chapter_number, image, image_blob, description, views, rating, updated_at, external_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), nextval('app_truyen_story_external_id_seq'::regclass));
                """
                cursor.execute(query, (
                    story_name,                              # title
                    thong_tin_truyen["ten_truyen_full"],     # title_full
                    thong_tin_truyen["tac_gia"],             # author
                    thong_tin_truyen["trang_thai"],          # status
                    total_chapters,                          # chapter_number
                    thong_tin_truyen["image"],               # image
                    psycopg2.Binary(thong_tin_truyen["image_blob"]),  # image_blob
                    thong_tin_truyen["description_html"],    # description
                    0,                                       # views
                    thong_tin_truyen["rating_value"]         # rating
                ))
                print(f"Đã thêm mới truyện: {story_name}")

            # Commit thay đổi
            conn.commit()

        else:
            print("Không thể lấy thông tin truyện.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Lỗi khi crawl truyện {story_name}: {e}")
        raise
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()


# Hàm tạo link chương
import os
import logging

def generate_links(cursor, story_name, total_chapters):
    try:
        # Truy vấn để lấy các chương bị thiếu
        query = """
        WITH missing_chapters AS (
            SELECT 
                s.title AS story_title,
                generate_series(1, s.chapter_number) AS chapter_number
            FROM 
                app_truyen_story s
            WHERE 
                s.title = %s
                AND s.chapter_number < 10000
        )
        SELECT 
            mc.chapter_number
        FROM 
            missing_chapters mc
        LEFT JOIN 
            app_truyen_chapter c 
        ON 
            mc.story_title = c.story_id
            AND mc.chapter_number = c.chapter_number
        WHERE 
            c.chapter_number IS NULL;
        """
        cursor.execute(query, (story_name,))
        missing_chapters = [row[0] for row in cursor.fetchall()]

        # Tạo thư mục missingchapter nếu chưa tồn tại
        os.makedirs("missingchapter", exist_ok=True)

        # Tạo đường dẫn file lưu link chương
        output_file = os.path.join("missingchapter", f"{story_name}.txt")

        # Ghi link chương vào file
        with open(output_file, "w", encoding="utf-8") as file:
            # Ghi các chương bị thiếu vào file (nếu có)
            if missing_chapters:
                # file.write("\n# Các chương bị thiếu:\n")
                for chapter in missing_chapters:
                    link = f"https://{CRAWL_URL}/{story_name}/chuong-{chapter}"
                    file.write(link + "\n")

        print(f"Đã tạo links cho truyện: {story_name}")
        if missing_chapters:
            print(f"Các chương bị thiếu đã được ghi vào file: {missing_chapters}")
        else:
            print("Không có chương nào bị thiếu.")

    except Exception as e:
        logging.error(f"Lỗi khi tạo links cho truyện {story_name}: {e}")
        raise


def process_list():
    try:
        # Kết nối database (không cần password vì dùng .pgpass)
        conn = psycopg2.connect(
            dbname="defaultdb",
            host="truyenso-do-user-14364101-0.m.db.ondigitalocean.com",
            port=25060,
            user="doadmin"
        )
        cursor = conn.cursor()

        # Đọc file listtruyen.txt
        with open("listtruyen.txt", "r", encoding="utf-8") as infile:
            for line in infile:
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    story_name, total_chapters = line.split()
                    
                    # Kiểm tra tồn tại
                    print(check_story_exists(story_name, cursor))
                    is_exist = check_story_exists(story_name, cursor)
                    is_update = IS_UPDATE
                    if not is_exist and not is_update:
                        print(f"Truyện {story_name} chưa tồn tại. Tiến hành crawl.")
                        crawl_story(story_name, total_chapters)
                        print(f"Đã insert truyện {story_name} vào database.")
                    elif is_exist and is_update:
                        print(f"Truyện {story_name} can update thong tin.")
                        crawl_story(story_name, total_chapters)
                        print(f"Đã update thong tin truyện {story_name} vào database.")
                    else:
                        print(f"Truyện {story_name} đã tồn tại. Tiến hành tạo links.")
                    
                    # Tạo links
                    if not is_update:
                        generate_links(cursor, story_name, total_chapters)
                
                except Exception as e:
                    logging.error(f"Lỗi khi xử lý dòng '{line}': {e}")
                    continue  # Bỏ qua lỗi và tiếp tục dòng tiếp theo

    except Exception as e:
        logging.error(f"Lỗi khi kết nối database: {e}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()


# Hàm sử dụng httrack để tải nội dung trang web
def crawl_truyen(url, output_dir="truyen_info"):
    """
    Sử dụng httrack để tải trang web từ URL.
    
    Args:
        url (str): URL của truyện cần tải.
        output_dir (str): Thư mục lưu nội dung tải về.
    """
    try:
        # Tạo thư mục lưu trữ nếu chưa tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Dùng httrack để tải trang
        subprocess.run(
            ["httrack", url, "-O", output_dir, "-r1", "--mirror"],
            check=True
        )
        print(f"Đã tải xong nội dung từ {url} và lưu vào {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi crawl {url}: {e}")
        return None

# Hàm đọc nội dung tải về và lấy thông tin truyện
def extract_truyen_info(output_dir, url):
    """
    Lấy thông tin truyện từ nội dung tải về bằng httrack.
    
    Args:
        output_dir (str): Thư mục chứa nội dung đã tải.
        url (str): URL của truyện cần lấy thông tin.
    
    Returns:
        dict: Thông tin truyện hoặc None nếu không thành công.
    """
    try:
        # Xác định file index.html tương ứng với URL
        domain = url.split("//")[-1].split("/")[0]  # Lấy tên miền
        story_slug = url.rstrip("/").split("/")[-1]  # Lấy slug của truyện
        index_path = os.path.join(output_dir, domain, story_slug, "index.html")
        
        if not os.path.exists(index_path):
            print(f"Không tìm thấy file index.html trong {index_path}")
            return None

        # Đọc nội dung file index.html
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Gọi hàm lay_thong_tin_truyen để phân tích nội dung
        return lay_thong_tin_truyen_from_html(html_content)
    except Exception as e:
        print(f"Lỗi khi xử lý nội dung từ {url}: {e}")
        return None

# Hàm phân tích nội dung HTML để lấy thông tin truyện
def lay_thong_tin_truyen_from_html(html_content):
    """
    Lấy thông tin truyện từ nội dung HTML.
    
    Args:
        html_content (str): Nội dung HTML của trang.
    
    Returns:
        dict: Thông tin truyện.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Lấy tiêu đề truyện
        ten_truyen_full = soup.find('h3', class_='title').get_text(strip=True) if soup.find('h3', class_='title') else None
        print(f"ten_truyen_full: {ten_truyen_full}")

        # Lấy tác giả
        tac_gia = soup.find('a', {'itemprop': 'author'}).get_text(strip=True) if soup.find('a', {'itemprop': 'author'}) else None
        print(f"tac_gia: {tac_gia}")

        # Thể loại
        the_loai = 'Tiên Hiệp'  # Tạm thời cố định
        print(f"the_loai: {the_loai}")

        # Trạng thái
        trang_thai = soup.find('span', class_='text-primary').get_text(strip=True) if soup.find('span', class_='text-primary') else None
        if trang_thai is None:
            # Tìm trạng thái (status)
            status_tag = soup.find('span', class_='text-success')
            print(status_tag)
            status = status_tag.get_text(strip=True) if status_tag else None
            trang_thai = status
            print(f"status: {status}")
        print(f"trang_thai: {trang_thai}")

        # Số chương
        so_chuong = None
        print(f"so_chuong: {so_chuong}")

        # Lấy link ảnh và tải ảnh
        image_blob = None
        image = soup.find('img', itemprop='image')
        if image:
            image_src = image['src']
            print("Link ảnh:", image_src)

            # Tải ảnh
            response = requests.get(image_src)
            if response.status_code == 200:
                image_blob = response.content
                print(f"Ảnh đã được tải về. Kích thước: {len(image_blob)} bytes")
            else:
                print("Không thể tải ảnh, lỗi HTTP:", response.status_code)
        else:
            print("Không tìm thấy ảnh.")

        # Xử lý mô tả
        description_html = soup.find('div', class_='desc-text desc-text-full').prettify() if soup.find('div', class_='desc-text desc-text-full') else None
        if description_html is None:
            description_html = soup.find('div', class_='desc-text').prettify() if soup.find('div', class_='desc-text') else None
        description_html = re.sub(r"truyenfull", "truyenso", description_html) if description_html else None
        if description_html is None:
            print(f"description_html: None")
        else:
            print(f"description_html: get successfully.")

        # Lấy đánh giá
        rating_tag = soup.find("span", itemprop="ratingValue")
        rating_value = float(rating_tag.text) if rating_tag else 0.0
        print(f"rating_value: {rating_value}")

        # Lấy số lượt
        rating_count = None
        rating_count_tag = soup.find('span', itemprop='ratingCount')
        if rating_count_tag:
            rating_count = int(rating_count_tag.text.strip())
            print("Số lượt:", rating_count)
        else:
            print("Không tìm thấy số lượt.")

        # Trả về kết quả
        return {
            "ten_truyen_full": ten_truyen_full,
            "tac_gia": tac_gia,
            "the_loai": the_loai,
            "trang_thai": trang_thai,
            "so_chuong": so_chuong,
            "image": image_src,                      # URL ảnh
            "image_blob": image_blob,                # Dữ liệu nhị phân của ảnh
            "description_html": description_html,    # Mô tả
            "rating_value": rating_value,            # Đánh giá
            "so_luot": rating_count                  # Số lượt
        }

    except Exception as e:
        print(f"Lỗi khi phân tích nội dung HTML: {e}")
        return None

import os

def read_missing_chapters(directory="missingchapter"):
    try:
        # Kiểm tra nếu thư mục tồn tại
        if not os.path.exists(directory):
            print(f"Thư mục {directory} không tồn tại.")
            return

        # Lấy danh sách tất cả các file trong thư mục
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        if not files:
            print(f"Không có file nào trong thư mục {directory}.")
            return

        # Đọc lần lượt từng file
        for file_name in files:
            file_path = os.path.join(directory, file_name)
            print(f"Đọc nội dung từ file: {file_name}")
            
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.readlines()
            
            # Xử lý nội dung từng dòng
            for line in content:
                line = line.strip()
                if not line:
                    continue  # Bỏ qua dòng trống
                run_crawl_chapter_script(line)
                
            
        
        print("Đã đọc xong tất cả các file.")
    except Exception as e:
        print(f"Lỗi khi đọc file trong thư mục {directory}: {e}")
        raise
    

def run_crawl_chapter_script(url):
    try:
        # Đường dẫn tới script shell
        script = "./crawl_chapter.sh"

        # Thực hiện lệnh shell
        with open("error.log", "w") as error_log:
            result = subprocess.run(
                [script, url],          # Lệnh và tham số
                stdout=error_log,       # Ghi stdout vào error.log
                stderr=subprocess.STDOUT, # Ghi stderr vào cùng error.log
                check=True              # Raise exception nếu lệnh trả về mã lỗi
            )
        
        print(f"Script chạy thành công với URL: {url}")

    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy script: {e}")
    except FileNotFoundError:
        print(f"Không tìm thấy script {script}. Kiểm tra đường dẫn!")
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        
# Hàm để lặp qua các thư mục con của 'tien-nghich', tìm thư mục 'truyenfull.bio', và xử lý file index.html
def process_truyen(root_dir, sql_file):
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path):
            # Kiểm tra nếu thư mục con chứa 'truyenfull.bio'
            truyenfull_path = os.path.join(subdir_path, CRAWL_URL)
            if os.path.exists(truyenfull_path) and os.path.isdir(truyenfull_path):
                truyen_title = os.listdir(truyenfull_path)[0] 
                for dirpath, _, files in os.walk(truyenfull_path):
                    for file in files:
                        if file == "index.html":
                            index_path = os.path.join(dirpath, file)
                            try:
                                with open(index_path, "r", encoding="utf-8", errors='ignore') as html_file:
                                    soup = BeautifulSoup(html_file, "html.parser")

                                    # Lấy title, số chương, và nội dung
                                    chapter_title_element = soup.find('h2')
                                    if not chapter_title_element:
                                        # print("Chapter title not found")
                                        continue
                                    chapter_title = chapter_title_element.find('a', class_='chapter-title')
                                    chapter_title = chapter_title.get_text(strip=True) if chapter_title else "Untitled Chapter"
                                    chapter_title = re.sub(r"Chương(\d+)", r"Chương \1", chapter_title)

                                    # Sử dụng regex để tìm số sau chữ "Chương"
                                    match = re.search(r"Chương\s*(\d+)", chapter_title)
                                    if match:
                                        chapter_number = int(match.group(1))
                                    else:
                                        # print("Không tìm thấy số chương.")
                                        chapter_number = 0

                                    chapter_content = soup.find(class_="chapter-c")
                                    # content = chapter_content.get_text(separator='\n', strip=True) if chapter_content else ""
                                    story_id = truyen_title
                                    story_chapter = re.sub(r"_chuong-", "_", subdir)

                                    if chapter_title and chapter_content and chapter_number != 0:
                                        save_to_sql(sql_file, story_chapter, chapter_title, chapter_number, chapter_content, story_id)
                            except Exception as e:
                                print(f"Lỗi khi xử lý file {index_path}: {e}")
                                continue

def balance_single_quotes(content):
    # Pattern: Match groups of single quotes
    pattern = r"'{1,}"
    
    def replace_quotes(match):
        # Get the matched single quotes
        quotes = match.group(0)
        # If the number of quotes is odd, add one more
        if len(quotes) % 2 != 0:
            return quotes + "'"
        return quotes
    
    # Use re.sub with the custom replace function
    return re.sub(pattern, replace_quotes, content)

def replace_single_quotes(content):
    # Pattern: Match a substring starting with a space, letter, or digit followed by a single quote
    pattern = r"(?<=[^'])'"
    # Replace with two single quotes
    return re.sub(pattern, "''", content)

# Hàm để lưu hoặc cập nhật dữ liệu vào file SQL
def save_to_sql(sql_file, story_chapter, title, chapter_number, content, story_id):
# Chuyển đổi \n thành <br> để hiển thị đúng trong trình duyệt
    # content_html = content.replace("\n", "<br>")
    content = str(content) if content else "<p>Nội dung không có</p>"
    safe_content = balance_single_quotes(content)
    safe_story_chapter = balance_single_quotes(story_chapter)
    safe_title = balance_single_quotes(title)
    safe_story_id = balance_single_quotes(story_id)
    sql_query = (
        f"INSERT INTO app_truyen_chapter (story_chapter, title, content, chapter_number, views, updated_at, story_id) "
        f"VALUES ('{safe_story_chapter}', '{safe_title}', '{safe_content}', {chapter_number}, 0, NOW(), '{safe_story_id}') "
        f"ON CONFLICT (story_chapter) DO UPDATE SET title = EXCLUDED.title, content = EXCLUDED.content, updated_at = EXCLUDED.updated_at;"
    )
    with open(sql_file, "a", encoding="utf-8") as f:
        f.write(sql_query + "\n")
        
def execute_sql_inserts(cursor, sql_file_path):
    try:
        # Đọc nội dung file SQL
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Phân tách các câu lệnh SQL (giả định sử dụng dấu chấm phẩy `;` để kết thúc mỗi câu lệnh)
        sql_statements = sql_content.split(';')
        
        # Thực thi từng câu lệnh
        for statement in sql_statements:
            statement = statement.strip()  # Loại bỏ khoảng trắng thừa
            if statement:  # Bỏ qua câu lệnh rỗng
                cursor.execute(statement)
        
        print("Tất cả các câu lệnh INSERT đã được thực thi thành công.")
    except Exception as e:
        print(f"Lỗi khi thực thi câu lệnh SQL: {e}")
        raise
import subprocess

def import_sql_file(sql_file, user, host, port, database):
    try:
        # Lệnh psql với các tham số
        command = [
            "psql",
            "-U", user,
            "-h", host,
            "-p", port,
            "-d", database,
            "--set", "sslmode=require",
            "--set", "ON_ERROR_STOP=off",
            "-f", sql_file
        ]

        # Thực thi lệnh
        result = subprocess.run(
            command,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print(f"SQL file '{sql_file}' đã được import thành công.")
        print(f"Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy lệnh psql: {e}")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
    except FileNotFoundError:
        print("Lệnh psql không được tìm thấy. Hãy kiểm tra xem PostgreSQL đã được cài đặt và lệnh psql có trong PATH hay chưa.")
    except Exception as e:
        print(f"Lỗi không xác định: {e}")



def update_story_external_id(cursor, story_title):
    try:
        # Câu lệnh SQL
        sql = """
        UPDATE app_truyen_chapter
        SET story_external_id = (
            SELECT external_id 
            FROM app_truyen_story 
            WHERE app_truyen_story.title = %s
        )
        WHERE story_id = %s;
        """
        
        # Thực thi câu lệnh với tham số truyền vào
        cursor.execute(sql, (story_title, story_title))
        print(f"Cập nhật thành công story_external_id cho story_id: {story_title}.")
    except Exception as e:
        print(f"Lỗi khi thực thi câu lệnh UPDATE: {e}")
        raise
    
def process_stories_from_file(file_path, cursor):
    try:
        # Đọc file listtruyen.txt
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Lặp qua từng dòng
        for line in lines:
            line = line.strip()
            if not line:
                continue  # Bỏ qua dòng trống

            # Tách tên truyện và số chương
            story_details = line.split()
            story_title = story_details[0] if story_details else None

            if story_title:
                print(f"Đang xử lý truyện: {story_title}")
                # Gọi hàm update_story_external_id
                update_story_external_id(cursor, story_title=story_title)

        print("Đã xử lý xong tất cả các truyện trong file.")
    except Exception as e:
        print(f"Lỗi khi xử lý file {file_path}: {e}")
        raise




if __name__ == "__main__":
    # 1. Nhap danh sach truyen muon crawl vao file listtruyen.txt
    # 2. Lap file listtruyen.txt
    # 3. Doi voi moi truyen trong listruyen thi kiem tra truyen co ton tai trong bang app_truyen_story hay chua, neu chua thi lay thong tin va insert vao
    # 4. Sau khi insert xong thi tao file chua link chuong cua truyen
    # 5. Nhung chuong truyen con thieu duoc luu vao file rieng voi ten ten-truyen.txt trong thu muc missingchapter
    process_list()
    if not IS_UPDATE:
        # 6. Thuc hien doc lan luot tung file trong thu muc missingchapter
        read_missing_chapters()
        # Thư mục gốc là thư mục cùng cấp với file này
        root_directory = "httrack_output"
        print(root_directory)
        # File để lưu câu lệnh SQL
        sql_file_path = "missingchapter.sql"

        # Xóa file nếu đã tồn tại để tránh trùng lặp nội dung
        if os.path.exists(sql_file_path):
            os.remove(sql_file_path)

        # Gọi hàm xử lý
        process_truyen(root_directory, sql_file_path)
        print(f"Hoàn thành! Câu lệnh SQL đã được lưu trong {sql_file_path}")
        # 7. Doi voi moi file dang doc thi lap qua cac chuong con thieu trong file va thuc hien cac viec sau.
        # - crawl toan bo cac chuong cua mot file ve 
        # - khi xong mot file thi xu ly du lieu crawl va luu vao database
        
        import_sql_file(sql_file_path, "doadmin", "truyenso-do-user-14364101-0.m.db.ondigitalocean.com", "25060", "defaultdb")
        
        # Kết nối cơ sở dữ liệu
        conn = psycopg2.connect(
            dbname="defaultdb",
            host="truyenso-do-user-14364101-0.m.db.ondigitalocean.com",
            port=25060,
            user="doadmin",
        )
        cursor = conn.cursor()

        # Gọi hàm để xử lý file và cập nhật
        try:
            process_stories_from_file('listtruyen.txt', cursor)
            conn.commit()  # Lưu thay đổi vào cơ sở dữ liệu
        except Exception as e:
            print(f"Lỗi trong quá trình xử lý: {e}")
        finally:
            cursor.close()
            conn.close()

    
    
