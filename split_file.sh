#!/bin/bash

# Kiểm tra nếu file đầu vào được truyền
if [ -z "$1" ]; then
    echo "Vui lòng truyền file đầu vào."
    exit 1
fi

# Đường dẫn file đầu vào
input_file="$1"

# Kiểm tra nếu file đầu vào tồn tại
if [ ! -f "$input_file" ]; then
    echo "File $input_file không tồn tại."
    exit 1
fi

# Số dòng tối đa mỗi file nhỏ
max_lines=1000

# Tên cơ sở cho các file nhỏ
base_name="truyen"

# Tách file thành các file nhỏ
split -l $max_lines -d -a 4 --additional-suffix=.txt "$input_file" ${base_name}_

# Đổi tên các file nhỏ theo định dạng truyen_x.txt
counter=1
for file in ${base_name}_*; do
    mv "$file" "${base_name}_${counter}.txt"
    ((counter++))
done

# Thông báo hoàn thành
echo "Đã tách file $input_file thành các file nhỏ với tối đa $max_lines dòng."
