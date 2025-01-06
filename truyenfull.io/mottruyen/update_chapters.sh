#!/bin/bash

# Kiểm tra nếu không đủ tham số
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <sql_file> <story_key>"
  exit 1
fi

# Lấy giá trị từ tham số dòng lệnh
SQL_FILE="$1.sql"
STORY_KEY="$1"

# Đặt các biến khác cho thông tin kết nối
PGPASSWORD="AVNS_DEdTlqbQ6a6cbgv-noq"
USER="doadmin"
HOST="truyenso-do-user-14364101-0.m.db.ondigitalocean.com"
PORT="25060"
DATABASE="defaultdb"

# Chạy lệnh import file SQL
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DATABASE" --set=sslmode=require --set=ON_ERROR_STOP=off -f "$SQL_FILE"

# Chạy lệnh UPDATE với câu lệnh mới
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DATABASE" --set=sslmode=require <<EOF
WITH story_data AS (
    SELECT external_id, title
    FROM app_truyen_story
    WHERE title = '${STORY_KEY}'
)
UPDATE app_truyen_chapter AS c
SET 
    story_id = s.title,
    story_external_id = sd.external_id
FROM app_truyen_story AS s, story_data AS sd
WHERE c.story_chapter LIKE s.title || '\_%'
  AND c.story_chapter LIKE '${STORY_KEY}' || '\_%'
  AND s.title = sd.title;
EOF

