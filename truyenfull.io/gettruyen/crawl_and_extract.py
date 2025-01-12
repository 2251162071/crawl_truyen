import os, re
import subprocess
from bs4 import BeautifulSoup
import requests

# Hàm sử dụng httrack để tải nội dung trang web
def crawl_truyen(url, output_dir="httrack_output"):
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

        ten_truyen_full = soup.find('h3', class_='title').get_text(strip=True) if soup.find('h3', class_='title') else None
        tac_gia = soup.find('a', {'itemprop': 'author'}).get_text(strip=True) if soup.find('a', {'itemprop': 'author'}) else None
        the_loai = 'Tiên Hiệp'  # Tạm thời cố định
        trang_thai = soup.find('span', class_='text-primary').get_text(strip=True) if soup.find('span', class_='text-primary') else None
        so_chuong = None
        description_html = soup.find('div', class_='desc-text desc-text-full').prettify() if soup.find('div', class_='desc-text desc-text-full') else None
        description_html = re.sub(r"truyenfull", "truyenso", description_html)
        rating_tag = soup.find("span", itemprop="ratingValue")
        rating_value = float(rating_tag.text) if rating_tag else 0.0

        return {
            "ten_truyen_full": ten_truyen_full,
            "tac_gia": tac_gia,
            "the_loai": the_loai,
            "trang_thai": trang_thai,
            "so_chuong": so_chuong,
            "description_html": description_html,
            "rating_value": rating_value
        }
    except Exception as e:
        print(f"Lỗi khi phân tích nội dung HTML: {e}")
        return None

if __name__ == "__main__":
    # URL cần crawl
    url = "https://truyenfull.io/tien-nghich/"
    
    # Thư mục lưu nội dung tải về
    output_dir = "httrack_output"
    
    # Bước 1: Tải nội dung từ URL
    crawl_truyen(url, output_dir)
    
    # Bước 2: Lấy thông tin truyện từ nội dung đã tải
    thong_tin_truyen = extract_truyen_info(output_dir, url)
    
    if thong_tin_truyen:
        print("Thông tin truyện:", thong_tin_truyen)
    else:
        print("Không thể lấy thông tin truyện.")
