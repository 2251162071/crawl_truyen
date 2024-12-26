#!/bin/bash

# Đường dẫn thư mục httrack_output
HTTRACK_DIR="$(dirname "$0")/httrack_output"
OUTPUT_FILE="$(dirname "$0")/list_rong.txt"

# Xóa file list_rong.txt nếu đã tồn tại
> "$OUTPUT_FILE"

# Kiểm tra sự tồn tại của thư mục httrack_output
if [ ! -d "$HTTRACK_DIR" ]; then
  echo "Thư mục httrack_output không tồn tại." >&2
  exit 1
fi

# Duyệt qua các thư mục con trong httrack_output
for dir in "$HTTRACK_DIR"/*; do
  if [ -d "$dir" ]; then
    base_dir_name=$(basename "$dir")

    # Kiểm tra cấu trúc thư mục
    if [[ "$base_dir_name" =~ ^(.+)_chuong-([0-9]+)$ ]]; then
      ten_truyen="${BASH_REMATCH[1]}"
      chuong="chuong-${BASH_REMATCH[2]}"

      # Kiểm tra thư mục truyenfull.io
      truyenfull_dir="$dir/truyenfull.io"
      if [ ! -d "$truyenfull_dir" ]; then
        echo "$base_dir_name" >> "$OUTPUT_FILE"
        continue
      fi

      # Kiểm tra thư mục ten-truyen
      ten_truyen_dir="$truyenfull_dir/$ten_truyen"
      if [ ! -d "$ten_truyen_dir" ]; then
        echo "$base_dir_name" >> "$OUTPUT_FILE"
        continue
      fi

      # Kiểm tra thư mục chuong-x
      chuong_dir="$ten_truyen_dir/$chuong"
      if [ ! -d "$chuong_dir" ]; then
        echo "$base_dir_name" >> "$OUTPUT_FILE"
      fi
    fi
  fi

done

echo "Kiểm tra hoàn tất. Kết quả lưu trong $OUTPUT_FILE."

