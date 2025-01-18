#!/bin/bash

# Kiểm tra nếu tham số không được truyền
if [ -z "$1" ]; then
    echo "Vui lòng truyền một URL."
    exit 1
fi

# URL được truyền vào từ tham số
URL="$1"

# Thư mục lưu kết quả tải
OUTPUT_DIR="httrack_output"

# File log ghi lại các lỗi
ERROR_LOG="error.log"

# Xóa file log cũ nếu có
> "$ERROR_LOG"

# Kiểm tra nếu URL không rỗng
if [[ -n "$URL" ]]; then
    echo "Đang xử lý URL: $URL"

    # Tạo tên thư mục từ URL
    if [[ "$URL" =~ https?://[^/]+/([^/]+)/chuong-([0-9]+) ]]; then
        STORY_NAME="${BASH_REMATCH[1]}"   # Tên truyện từ URL
        CHAPTER="chuong-${BASH_REMATCH[2]}" # Chương từ URL
        URL_DIR="$OUTPUT_DIR/${STORY_NAME}_${CHAPTER}"
    else
        # Nếu không khớp format, dùng tên mặc định
        URL_DIR="$OUTPUT_DIR/$(echo "$URL" | sed -E 's|https?://||; s|/$||; s|/|_|g')"
    fi

    # Kiểm tra nếu thư mục đã tồn tại
    if [ -d "$URL_DIR" ]; then
        echo "Thư mục $URL_DIR đã tồn tại. Bỏ qua việc tải."
    else
        # Đảm bảo thư mục lưu trữ tồn tại
        mkdir -p "$URL_DIR"
        echo "Bắt đầu tải: $URL"
        httrack "$URL" -O "$URL_DIR" -r1
    fi
fi

echo "Quá trình hoàn tất. Kiểm tra lỗi trong $ERROR_LOG nếu cần."

