import re
from bs4 import BeautifulSoup

def extract_specific_links_from_chapters(file_path, output_file):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    
    # Tìm thẻ div với id="chapters"
    chapters_div = soup.find('div', id='chapters')
    
    if chapters_div:
        # Lọc các link có dạng https://dtruyen.net/luoc-thien-ky/*.html
        pattern = re.compile(r'^https://dtruyen\.net/luoc-thien-ky/.*\.html$')
        links = [a['href'] for a in chapters_div.find_all('a', href=True) if pattern.match(a['href'])]
        
        # Lưu vào tệp
        with open(output_file, 'w', encoding='utf-8') as out_file:
            for link in links:
                out_file.write(link + '\n')
        print(f"Đã lưu {len(links)} liên kết từ div#chapters vào tệp {output_file}.")
    else:
        print("Không tìm thấy thẻ div với id='chapters' trong tệp HTML.")

file_path = 'luoc-thien-ky.html'  # Thay đổi thành đường dẫn đúng nếu cần
output_file = 'luoc-thien-ky.txt'

extract_specific_links_from_chapters(file_path, output_file)
