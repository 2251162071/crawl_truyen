#!/bin/bash

# Khởi động ssh-agent
eval "$(ssh-agent -s)"

# Thêm SSH key
ssh-add ~/.ssh/Chat1

# Di chuyển đến thư mục crawl_truyen
cd ~/crawl_truyen

# Kích hoạt virtual environment
source venv/bin/activate

cp data/daucach/truyen_1.txt truyenfull.io/gettruyen/

# Di chuyển đến thư mục gettruyen
cd truyenfull.io/gettruyen

