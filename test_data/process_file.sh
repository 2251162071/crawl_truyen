#!/bin/bash

# Đường dẫn đến file
file_path="truyen_8.txt"

# Loại bỏ những dòng mà sau dấu : không phải là số
filtered_file=$(awk -F: '/^[^:]+:[0-9]+$/' "$file_path")

# Tính tổng các số sau dấu :
total=$(echo "$filtered_file" | awk -F: '{sum += $2} END {print sum}')

# In kết quả ra màn hình
echo "Tổng giá trị các số sau dấu : là: $total"

