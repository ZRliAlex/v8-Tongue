#! /bin/bash
cd /home/medcv/tongue/tongue_server_v8s_24_06_25
source ~/.bashrc
source activate torch
ulimit -c unlimited
pkill -f tong_seg_server_v2.py
python -u ./tong_seg_server_v2.py > record.log 2>&1 &

exit 0
