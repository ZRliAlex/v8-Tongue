#! /bin/bash
LOGPATH=/home/medcv/tongue/tongue_server_v8s_24_06_25/tongseg_server_monitor.log

# Add debug info
echo `date` +": Tong seg model test started" >> $LOGPATH
printenv >> $LOGPATH

# Check tong_seg_server_v2.py process
runcount=`ps -ef | grep "tong_seg_server_v2.py" | grep -v grep | wc -l`
if [ $runcount -lt 1 ] ; then
    echo `date` +": Warning run_data_httpserver is not running, restart..........." >> $LOGPATH
    cd /home/medcv/tongue/tongue_server_v8s_24_06_25 || { echo `date` +": cd failed" >> $LOGPATH; exit 1; }
    source /home/medcv/miniconda3/bin/activate torch || { echo `date` +": conda activate failed" >> $LOGPATH; exit 1; }
    nohup python ./tong_seg_server_v2.py > record.log 2>&1 &
    if [ $? -eq 0 ]; then
        echo `date` +": Successfully restarted tong_seg_server_v2.py" >> $LOGPATH
    else
        echo `date` +": Failed to restart tong_seg_server_v2.py" >> $LOGPATH
    fi
else
    echo `date` +": ok" >> $LOGPATH
fi

# Add debug info
echo `date` +": Tong seg model test ended" >> $LOGPATH

exit 0
