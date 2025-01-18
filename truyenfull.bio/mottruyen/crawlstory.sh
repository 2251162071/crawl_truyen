#!/bin/bash

# Kiểm tra xem người dùng có cung cấp đủ tham số không
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <story_id> <batch_number>"
    exit 1
fi

STORY_ID="$1"
BATCH_NUMBER="$2"

echo "Fetching story..."
./1fetch_truyen.sh "$STORY_ID" "$BATCH_NUMBER"

echo "Crawling story..."
python 2batch_crawl.py "${STORY_ID}_${BATCH_NUMBER}" > error.log 2>&1 

echo "Extracting chapters..."
python extract_chapter.py "$STORY_ID"

echo "Updating chapters..."
./update_chapters.sh "$STORY_ID"

echo "Process completed!"

