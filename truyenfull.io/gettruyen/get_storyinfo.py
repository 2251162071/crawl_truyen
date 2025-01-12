def lay_thong_tin_truyen(url):
    """
    Lấy thông tin truyện từ URL của truyện.
    
    Args:
        url (str): URL của truyện cần lấy thông tin.
        'https://example.com/ten-truyen/'
    
    Returns:
        dict: Thông tin truyện từ URL.
        {'ten_truyen_full': 'Tên truyện', 'tac_gia': 'Tác giả', 'the_loai': 'Thể loại', 'trang_thai': 'Trạng thái', 'so_chuong': 'Số chương', 'description_html': 'Mô tả truyện', 'rating_value': 'Đánh giá'}
    """
    try:
        response = utils.send_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')


        ten_truyen_full = None
        if soup.find('h3', class_='title') is not None:
            ten_truyen_full = soup.find('h3', class_='title').get_text(strip=True)
        # print(Fore.RED + f"ten_truyen_full: {ten_truyen_full}")
        tac_gia = None
        if soup.find('a', {'itemprop': 'author'}) is not None:
            tac_gia = soup.find('a', {'itemprop': 'author'}).get_text(strip=True)
        # print(Fore.RED + f"tac_gia: {tac_gia}")
        the_loai = 'Tiên Hiệp' # TODO: Tạm thời để cố định
        trang_thai = None
        if soup.find('span', class_='text-primary') is not None:
            trang_thai = soup.find('span', class_='text-primary').get_text(strip=True)
        elif soup.find('span', class_='text-success') is not None:
            trang_thai = soup.find('span', class_='text-success').get_text(strip=True)
        elif soup.find('span', class_='label-hot') is not None:
            trang_thai = 'Hot'
        # print(Fore.RED + f"trang_thai: {trang_thai}")
        so_chuong = None
        description_html = None
        if soup.find('div', class_='desc-text desc-text-full') is None:
            description_html = soup.find('div', {'itemprop': 'description'}).prettify()
        else:
            description_html = soup.find('div', class_='desc-text desc-text-full').prettify()
        # print(Fore.RED + f"description_html: {description_html}")
        # Lấy ratingValue nếu có
        rating_tag = soup.find("span", itemprop="ratingValue")
        # print(Fore.RED + f"rating_tag: {rating_tag}")
        rating_value = float(rating_tag.text) if rating_tag else 0.0
        # print(Fore.RED + f"rating_value: {rating_value}")
        thong_tin_truyen = {
            "ten_truyen_full": ten_truyen_full,
            "tac_gia": tac_gia,
            "the_loai": the_loai,
            "trang_thai": trang_thai,
            "so_chuong": so_chuong,
            "description_html": description_html,
            "rating_value": rating_value
        }
        # print(Fore.GREEN + f"Lấy thông tin truyện {ten_truyen_full} thành công.")
        utils.log_with_color(f"Lấy thông tin truyện {ten_truyen_full} thành công.", Fore.GREEN)
        return thong_tin_truyen
    except requests.RequestException as e:
        # print(Fore.RED + f"Lỗi khi lấy thông tin truyện từ {url}: {e}")
        utils.log_with_color(f"Lỗi khi lấy thông tin truyện từ {url}: {e}", Fore.RED)
    return None