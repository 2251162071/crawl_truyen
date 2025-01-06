#!/bin/bash

# Dừng script nếu xảy ra lỗi
set -e

# Xoa httrack_output
rm -rf httrack_output
# Script đầu vào
GENERATE_SCRIPT="./generate_links.sh"
PROCESS_SCRIPT="./process_links.sh"
EXTRACT_CHAPTER="python extract_chapter.py"
UPDATE_SCRIPT="./update_chapters.sh"

# Kiểm tra nếu các script tồn tại và có quyền thực thi
if [ ! -x "$GENERATE_SCRIPT" ]; then
    echo "Script $GENERATE_SCRIPT không tồn tại hoặc không có quyền thực thi."
    exit 1
fi

if [ ! -x "$PROCESS_SCRIPT" ]; then
    echo "Script $PROCESS_SCRIPT không tồn tại hoặc không có quyền thực thi."
    exit 1
fi

if [ ! -x "$UPDATE_SCRIPT" ]; then
    echo "Script $UPDATE_SCRIPT không tồn tại hoặc không có quyền thực thi."
    exit 1
fi

# Chạy từng script theo thứ tự
echo "Chạy script: generate_links.sh"
$GENERATE_SCRIPT

echo "Chạy script: process_links.sh"
$PROCESS_SCRIPT

echo "Extract chapter: extract_chapter.py"
$EXTRACT_CHAPTER

echo "Chạy script: update_chapters.sh"
$UPDATE_SCRIPT

echo "Hoàn thành tất cả các script."

