#!/bin/bash

# Lấy giá trị từ tham số dòng lệnh
SQL_FILE="missingchapter.sql"

# Đặt các biến khác cho thông tin kết nối
USER="doadmin"
HOST="truyenso-do-user-14364101-0.m.db.ondigitalocean.com"
PORT="25060"
DATABASE="defaultdb"

# Chạy lệnh import file SQL
psql -U "$USER" -h "$HOST" -p "$PORT" -d "$DATABASE" --set=sslmode=require --set=ON_ERROR_STOP=off -f "$SQL_FILE"

