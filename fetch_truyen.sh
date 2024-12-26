#!/bin/bash

# Nhận tham số từ dòng lệnh
baseName="$1"
maxChuong="$2"

# Kiểm tra tham số
if [[ -z "$baseName" || -z "$maxChuong" ]]; then
    echo "Thiếu tham số đầu vào." >> error.log
    exit 0
fi

if ! [[ "$maxChuong" =~ ^[0-9]+$ ]] || [ "$maxChuong" -le 0 ]; then
    echo "Số chương phải là một số dương." >> error.log
    exit 0
fi

# Tạo baseUrl từ baseName
baseUrl="https://truyenfull.io/${baseName}/chuong-"

# Tên file đầu ra
outputFile="${baseName}_${maxChuong}.txt"

# Xóa file nếu đã tồn tại
if [ -f "$outputFile" ]; then
    rm "$outputFile"
fi

# Tạo danh sách link
for ((i=1; i<=maxChuong; i++)); do
    echo "${baseUrl}${i}/" >> "$outputFile"
done

echo "Danh sách link đã được lưu vào $outputFile"
