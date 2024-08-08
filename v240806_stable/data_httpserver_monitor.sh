#! /bin/bash
LOGPATH=/home/medcv/tongue/ton_seg_server/server_monitor.log
#check run_data_httpserver process
runcount=`ps -ef | grep "tong_seg_server.py"|grep -v grep |wc -l`
if [ $runcount -lt 1 ] ; then
	echo `date` +":Warning run_data_httpserver is not runnning ,restart..........." >> $LOGPATH
	cd /home/medcv/tongue/ton_seg_server
    source /home/medcv/miniconda3/bin/activate torch
	python -u ./tong_seg_server.py > record.log 2>&1 &
else
	echo `date` +":ok" >> $LOGPATH
fi

exit 1
