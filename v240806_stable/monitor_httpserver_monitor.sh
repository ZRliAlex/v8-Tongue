#! /bin/bash
LOGPATH=/home/medcv/monitor/monitor_server_monitor.log

# Add debug info
echo `date` +": Monitor test started" >> $LOGPATH
printenv >> $LOGPATH

# Check tong_seg_server_v2.py process
runcount=`ps -ef | grep "monitor.py" | grep -v grep | wc -l`
if [ $runcount -lt 1 ] ; then
    echo `date` +": Warning run_data_httpserver is not running, restart..........." >> $LOGPATH
    cd /home/medcv/monitor || { echo `date` +": cd failed" >> $LOGPATH; exit 1; }
    nohup python ./monitor.py > record.log 2>&1 &
    if [ $? -eq 0 ]; then
        echo `date` +": Successfully restarted monitor.py" >> $LOGPATH
    else
        echo `date` +": Failed to restart monitor.py" >> $LOGPATH
    fi
else
    echo `date` +": ok" >> $LOGPATH
fi

# Add debug info
echo `date` +": Monitor test ended " >> $LOGPATH
echo  "     " >> $LOGPATH

exit 0
