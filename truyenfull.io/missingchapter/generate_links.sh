#!/bin/bash

# Đường dẫn đến file đầu vào
input_file="chapterinfo.txt"
output_file="chapterlink.txt"

# Xóa file đầu ra nếu đã tồn tại
> "$output_file"

# Đọc từng dòng trong file
while IFS= read -r line; do
    # Tách tên truyện và số chương
    story=$(echo "$line" | awk '{print $1}')
    chapter=$(echo "$line" | awk '{print $2}')
    
    # Tạo link đầy đủ
    link="https://truyenfull.io/$story/chuong-$chapter"
    
    # Ghi vào file đầu ra
    echo "$link" >> "$output_file"
done < "$input_file"

echo "Links đã được tạo và lưu trong $output_file"

