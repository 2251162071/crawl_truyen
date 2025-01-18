#!/bin/bash

# File chứa danh sách URL
input_file="chapterlink.txt"

# Kiểm tra nếu file không tồn tại
if [ ! -f "$input_file" ]; then
    echo "File $input_file không tồn tại. Vui lòng kiểm tra."
    exit 1
fi

# Đọc từng dòng trong file
while IFS= read -r url; do
    # Bỏ qua dòng trống
    if [[ -n "$url" ]]; then
        # Gọi script crawl_chapter.sh với URL
	echo "Crawling $url"
        ./crawl_chapter.sh "$url" > error.log 2>&1
    fi
done < "$input_file"

echo "Tất cả các URL đã được xử lý."

