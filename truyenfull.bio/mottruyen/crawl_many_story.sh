#!/bin/bash

# Kiểm tra file tham số
PARAM_FILE="storyinfo.txt"

if [ ! -f "$PARAM_FILE" ]; then
    echo "Error: File $PARAM_FILE not found!"
    exit 1
fi

# Đọc từng dòng từ file và xử lý
while IFS= read -r line; do
    # Bỏ qua dòng trống
    if [[ -z "$line" ]]; then
        continue
    fi

    # Loại bỏ dấu cách thừa ở đầu và cuối dòng
    line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # Tách story_id và batch_number, bất kể có bao nhiêu dấu cách giữa chúng
    STORY_ID=$(echo "$line" | awk '{print $1}')
    BATCH_NUMBER=$(echo "$line" | awk '{print $NF}')

    echo "Processing story ID: $STORY_ID, Batch Number: $BATCH_NUMBER"
    ./crawlstory.sh "$STORY_ID" "$BATCH_NUMBER"
done < "$PARAM_FILE"

echo "All stories processed!"

