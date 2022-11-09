# !usr/bin/python3.6
 
import serial
import sys
import os
import time
import re
import serial.tools.list_ports
 
global MAX_LOOP_NUM
global newCmd
MAX_LOOP_NUM = 10
 
def waitForCmdOKRsp():
    maxloopNum = 0
    while True:
        line = ser.readline()                              #读取一行数据
        maxloopNum = maxloopNum + 1                        #计算读取长度
 
        try:
            print("Rsponse : %s" % line.decode('utf-8'))  #串口接收到数据，然后显示
        except:
            pass
        if (re.search(b'OK', line)):
            break
        elif (maxloopNum > MAX_LOOP_NUM):
            sys.exit(0)
 
def sendAT_Cmd(serInstance, atCmdStr, waitforOk):
   # print("Command: %s" % atCmdStr)
    serInstance.write(atCmdStr.encode('utf-8'))   # atCmdStr  波特率
    # or define b'string',bytes should be used not str

    if (waitforOk == 1):
        waitForCmdOKRsp()
    else:
        waitForCmdRsp()
 
plist = serial.tools.list_ports.comports() 
if len(plist) <= 0:
    print("没有发现端口!")
else:
    plist_0 = plist[-1]
    serialName = plist_0[0]       #先自动检测串口， 检测到可用串口，取出串口名
 
#ser = serial.Serial("COM6", 115200, timeout=30)
ser = serial.Serial(serialName, 38400, timeout=3)  # timeout=30 30s
print("可用端口名>>>", ser.name)
sendAT_Cmd(ser, 'AT+CFUN=1\r', 1)
ser.close()