import os
import re, sys
from bs4 import BeautifulSoup
# Hàm để lặp qua các thư mục con của 'tien-nghich', tìm thư mục 'truyenfull.io', và xử lý file index.html
def process_truyen(root_dir, sql_file):
    for subdir in os.listdir(root_dir):
        subdir_path = os.path.join(root_dir, subdir)
        if os.path.isdir(subdir_path):
            # Kiểm tra nếu thư mục con chứa 'truyenfull.io'
            truyenfull_path = os.path.join(subdir_path, "truyenfull.io")
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

if __name__ == "__main__":
    # Thư mục gốc là thư mục cùng cấp với file này
    root_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "httrack_output")
    print(root_directory)
    # File để lưu câu lệnh SQL
    sql_file_path = "missingchapter.sql"

    # Xóa file nếu đã tồn tại để tránh trùng lặp nội dung
    if os.path.exists(sql_file_path):
        os.remove(sql_file_path)

    # Gọi hàm xử lý
    process_truyen(root_directory, sql_file_path)
    print(f"Hoàn thành! Câu lệnh SQL đã được lưu trong {sql_file_path}")
