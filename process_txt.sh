#!/bin/bash

#Thư mục chứa các file .txt
directory="input_data"

# Khởi tạo biến tổng
total=0

# Duyệt qua tất cả các file .txt trong thư mục
for file in "$directory"/*.txt; do
# Đọc từng dòng trong file
     while IFS= read -r line; do
         # Kiểm tra xem dòng có đúng định dạng ten-truyen:x không
         if [[ $line =~ ^[a-zA-Z0-9_-]+:[0-9]+$ ]]; then
              # Tách phần số x bằng cách cắt chuỗi sau dấu ':'
              number=${line##*:}
              # Cộng dồn vào tổng
              total=$((total + number))
         fi
     done < "$file"
done

echo "Tổng các số x: $total"
