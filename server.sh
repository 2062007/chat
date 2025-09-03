#!/bin/bash
# server.sh - cài và chạy server chat

pip install --upgrade pip
pip install -r requirements.txt

# Xuất Redis URL (copy nguyên chuỗi từ Upstash dashboard)
export REDIS_URL="rediss://default:AZh5AAIncDFiOTAyMWFhMTBkMzA0MjlhYjJhY2JkNzgwZTQ0ZmEyMXAxMzkwMzM@concrete-worm-39033.upstash.io:6379"

python3 server.py

