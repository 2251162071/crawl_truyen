#!/bin/bash

# Thư mục chứa các file .txt (thư mục hiện tại)
folder_path=$(dirname "$0")

# Lặp qua tất cả các file .txt trong thư mục
for file in "$folder_path"/*.txt; do
    # Kiểm tra nếu file tồn tại
    if [ -f "$file" ]; then
        # Lọc những dòng hợp lệ (sau dấu : là số)
        filtered_lines=$(awk -F: '/^[^:]+:[0-9]+$/' "$file")

        # Tính tổng các số sau dấu :
        sum=$(echo "$filtered_lines" | awk -F: '{sum += $2} END {print sum}')

        # In tên file và tổng
        echo "File: $(basename "$file") - Tổng: $sum"
    fi
done

