import sys
import random
import time
import canopen as canopen
import minimalmodbus as minimalmodbus
import serial
import serial.tools.list_ports
from PyQt5 import  QtGui
from PyQt5 import  QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication
from mainPage import Ui_MainWindow
from PyQt5.QtCore import QThread ,  pyqtSignal,  QDateTime
import traceback
from PyQt5.QtWidgets import QMessageBox

#####################################################
#                    多线程区                        #
#####################################################
#为了处理后台时间较长的程序
class NodeIdDetetctThread(QThread):
    # 通过类成员对象定义信号对象  
    started = pyqtSignal()
    finished = pyqtSignal()
    # 处理要做的业务逻辑
    def run(self):
        self.started.emit()
        detectModBusID()
        self.finished.emit()

class configDeltaMotorThread(QThread):
    # 通过类成员对象定义信号对象  
    started = pyqtSignal()
    finished = pyqtSignal()
    # 处理要做的业务逻辑
    def run(self):
        self.started.emit()
        configDeltaMotor(PortNumber)
        self.finished.emit()
class CheckConfigModbusThread(QThread):
    # 通过类成员对象定义信号对象  
    started = pyqtSignal()
    finished = pyqtSignal()
    # 处理要做的业务逻辑
    def run(self):
        self.started.emit()
        mainUI.textBrowser.append(f"开始检测配置值")
        mainUI.textBrowser.append(f"------------------------")
        checkDeltaConfigInfo(PortNumber)
        mainUI.textBrowser.append(f"------------------------")
        mainUI.textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.finished.emit()
class configLifterThread(QThread):
    # 通过类成员对象定义信号对象  
    started = pyqtSignal()
    finished = pyqtSignal()
    # 处理要做的业务逻辑
    def run(self):
        self.started.emit()
        configLifter(PortNumber)
        self.finished.emit()

class CheckLifterConfigThread(QThread):
    # 通过类成员对象定义信号对象  
    started = pyqtSignal()
    finished = pyqtSignal()
    # 处理要做的业务逻辑
    def run(self):
        self.started.emit()
        mainUI.textBrowser.append(f"开始检测配置值")
        mainUI.textBrowser.append(f"------------------------")
        checkLifterConfigInfo(PortNumber)
        mainUI.textBrowser.append(f"------------------------")
        mainUI.textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.finished.emit()
        
#####################################################
#                    功能函数区                       #
#####################################################

# 获取端口号
def get_port_list():
    # 用于保存端口名的列表
    port_list = serial.tools.list_ports.comports()  # 获取本机端口，返回list
    return port_list  # 返回列表

def initModbusInterface(portNumber,nodeID):
    try:
        # modBus协议基本串口参数配置
        mainUI.textBrowser.append("初始化连接串口")
        instrument = minimalmodbus.Instrument(portNumber, nodeID)  # port name, slave address (in decimal)
        instrument.serial.baudrate = 38400
        instrument.serial.bytesize = 8
        instrument.serial.stopbits = 2
        instrument.serial.parity = serial.PARITY_NONE
        instrument.mode = minimalmodbus.MODE_RTU
        return instrument
    except Exception:
        mainUI.textBrowser.append("初始化串口失败，请检查连线是否已经插牢，或者串口是否选择错误")



#配置根据公司给出的参数表配置举升机
def configLifter(portNumber):
    for i in range(3):
        id = detectModBusID()
        if id != None:
            break
    if id == None:
        mainUI.textBrowser.append("全局ID检测失败")
    instrument = initModbusInterface(portNumber,id)
    try:
        mainUI.textBrowser.append("开始配置参数")
        # P1-01参数
        # 配置标准CANOpen通讯模式以及电机的转动方向。
        instrument.write_register(0x0102, 0x00c, 0, 6)
        # P1-52参数设置回生电阻值
        instrument.write_register(0x0168,0x40, 0, 6)
        # P1-53参数设置回生电阻容量
        instrument.write_register(0x016A, 0x40, 0, 6)
        # P2-10参数 备注DI1
        instrument.write_register(0x0214, 0x0, 0, 6)
        # P2-11参数 备注DI2
        instrument.write_register(0x0216, 0x0, 0, 6)
        # P2-12参数 备注DI3
        instrument.write_register(0x0218, 0x0, 0, 6)
        # P2-13参数 备注DI4
        instrument.write_register(0x021A, 0x0, 0, 6)
        # P2-14参数 备注DI5
        instrument.write_register(0x021C, 0x0, 0, 6)
        # P2-15参数 备注DI6
        instrument.write_register(0x021E, 0x0, 0, 6)
        # P2-16参数 备注DI7
        instrument.write_register(0x0220, 0x0, 0, 6)
        # P2-17参数 备注DI8
        instrument.write_register(0x0222, 0x0, 0, 6)
        # P3-00参数 备注举升机CANOpen node ID为1
        instrument.write_register(0x0300, 0x1, 0, 6)
        # P3-01参数 备注CANOpen 波特率CAN bus 1Mbps
        instrument.write_register(0x0302, 0x0403, 0, 6)
        # P3-09参数 CANOpen同步设定
        time.sleep(1)
        instrument.write_register(0x0312, 0x5055, 0, 6)
        mainUI.textBrowser.append("————————————————————————————")
        mainUI.textBrowser.append("配置成功！参数配置显示如下")
        time.sleep(1)
        readLifterConfig(instrument)
        mainUI.textBrowser.append("成功！请重新启动驱动器使配置生效")
        mainUI.textBrowser.append("————————————————————————————")
        mainUI.textBrowser.moveCursor(QtGui.QTextCursor.End)
    except Exception as e:
        mainUI.textBrowser.append("参数配置失败，请重试")
        mainUI.textBrowser.append("请检查是否有选择设备")
        traceback.print_exc()

#配置根据公司给出的参数表配置提升机
#传入参数为
def configDeltaMotor(portNumber):
    for i in range(3):
        id = detectModBusID()
        if id != None:
            break
    if id == None:
        mainUI.textBrowser.append("全局ID检测失败")

    instrument = initModbusInterface(portNumber,id)
    try:
        mainUI.textBrowser.append("开始配置参数")
        # P1-01参数
        # 标准CANOpen，需要根据提升机现场实际运行方向进行调整，配置值为0x000C或0x010C。向上提升方向为正。
        instrument.write_register(0x0102, 0x10c, 0, 6)
        # P1-42参数 刹车开启延时,单位ms
        instrument.write_register(0x0154,0x0, 0, 6)
        # P1-43参数 刹车关闭延时，单位ms
        instrument.write_register(0x0156,0x0, 0, 6)
        # P2-10参数 备注DI1
        instrument.write_register(0x0214, 0x0124, 0, 6)
        # P2-11参数 备注DI2
        instrument.write_register(0x0216, 0x0, 0, 6)
        # P2-12参数 备注DI3
        instrument.write_register(0x0218, 0x0, 0, 6)
        # P2-13参数 备注DI4
        instrument.write_register(0x021A, 0x0, 0, 6)
        # P2-14参数 备注DI5
        instrument.write_register(0x021C, 0x0, 0, 6)
        # P2-15参数 备注DI6
        instrument.write_register(0x021E, 0x0, 0, 6)
        # P2-16参数 备注DI7
        instrument.write_register(0x0220, 0x0, 0, 6)
        # P2-17参数 备注DI8只用于加保护传感器 默认值0x21，测试值0
        instrument.write_register(0x0222, SensorValue, 0, 6)
        # P2-18参数 备注Do1
        instrument.write_register(0x0224, 0x0, 0, 6)
        # P2-19参数 备注Do2
        instrument.write_register(0x0226, 0x0, 0, 6)
        # P2-20参数 备注Do3
        instrument.write_register(0x0228, 0x108, 0, 6)
        # P2-21参数 备注Do4
        instrument.write_register(0x022A, 0x0, 0, 6)
        # P2-22参数 备注Do5
        instrument.write_register(0x022C, 0x0, 0, 6)
        # P3-00参数 备注CANOpen node ID，上升列为1，下降列为2
        instrument.write_register(0x0300, NodeID, 0, 6)
        # P3-01参数 备注CANOpen 波特率CAN bus 250 Kbps
        instrument.write_register(0x0302, 0x0103, 0, 6)
        mainUI.textBrowser.append("————————————————————————————")
        mainUI.textBrowser.append("配置成功！参数配置显示如下")
        time.sleep(1)
        readDeltaConfig(instrument)
        mainUI.textBrowser.append("成功！请重新启动驱动器使配置生效")
        mainUI.textBrowser.append("————————————————————————————")
        mainUI.textBrowser.moveCursor(QtGui.QTextCursor.End)

    except Exception as e:
        mainUI.textBrowser.append("参数配置失败，请重试")
        mainUI.textBrowser.append("请检查是否有选择设备")
        traceback.print_exc()
        
def checkDeltaConfigInfo(portNumber):
    for i in range(3):
        id = detectModBusID()
        if id != None:
            break
    if id == None:
        mainUI.textBrowser.append("全局ID检测失败")
    instrument = initModbusInterface(portNumber,id)
    readDeltaConfig(instrument)

def readDeltaConfig(instrument):
    try:
        mainUI.textBrowser.append("当前提升机读取参数中")
        # P1-01参数
        # 标准CANOpen，需要根据提升机现场实际运行方向进行调整，配置值为0x000C或0x010C。向上提升方向为正。
        p1_01 = instrument.read_register(0x0102)
        mainUI.textBrowser.append(f"p1-01 = {hex(p1_01)}")
        # P1-42参数 刹车开启延时,单位ms
        p1_42 = instrument.read_register(0x0154)
        mainUI.textBrowser.append(f"p1-42 = {hex(p1_42)}")
        # P1-43参数 刹车关闭延时，单位ms
        p1_43 = instrument.read_register(0x0156)
        mainUI.textBrowser.append(f"p1-43 = {hex(p1_43)}")
        #读取提升机p2-10～p2-17参数
        readP2_10toP2_17Argu(instrument)
        # P2-18参数 备注Do1
        p2_18 = instrument.read_register(0x0224)
        mainUI.textBrowser.append(f"p2-18 = {hex(p2_18)}")
        # P2-19参数 备注Do2
        p2_19 = instrument.read_register(0x0226)
        mainUI.textBrowser.append(f"p2-19 = {hex(p2_19)}")
        # P2-20参数 备注Do3
        p2_20 = instrument.read_register(0x0228)
        mainUI.textBrowser.append(f"p2-20 = {hex(p2_20)}")
        # P2-21参数 备注Do4
        p2_21 = instrument.read_register(0x022A)
        mainUI.textBrowser.append(f"p2-21 = {hex(p2_21)}")
        # P2-22参数 备注Do5
        p2_22 = instrument.read_register(0x022C)
        mainUI.textBrowser.append(f"p2-22 = {hex(p2_22)}")
        # P3-00参数 备注CANOpen node ID，上升列为1，下降列为2
        p3_00 = instrument.read_register(0x0300)
        mainUI.textBrowser.append(f"p3-00 = {hex(p3_00)}")
        # P3-01参数 备注CANOpen 波特率CAN bus 250 Kbps
        p3_01 = instrument.read_register(0x0302)
        mainUI.textBrowser.append(f"p3-01 = {hex(p3_01)}")
        instrument.serial.close()
    except Exception:
        mainUI.textBrowser.append("参数读取失败，请重试,请排查串口是否错误！")
       

def checkLifterConfigInfo(portNumber):
    for i in range(3):
        id = detectModBusID()
        if id != None:
            break
    if id == None:
        mainUI.textBrowser.append("全局ID检测失败")
    instrument = initModbusInterface(portNumber,id)
    readLifterConfig(instrument)

def readLifterConfig(instrument):
    try:
        mainUI.textBrowser.append("当前举升机读取参数中")
        # P1-01参数
        # 标准CANOpen，需要根据提升机现场实际运行方向进行调整，配置值为0x000C或0x010C。向上提升方向为正。
        p1_01 = instrument.read_register(0x0102)
        mainUI.textBrowser.append(f"p1-01 = {hex(p1_01)}")
        # P1-52参数设置回生电阻值
        p1_52 =  instrument.read_register(0x0168)
        mainUI.textBrowser.append(f"p1-42 = {hex(p1_52)}")
        # P1-53参数设置回生电阻容量
        p1_53 =instrument.read_register(0x016A)
        mainUI.textBrowser.append(f"p1-43 = {hex(p1_53)}")
        #读取提升机p2-10～p2-17参数
        readP2_10toP2_17Argu(instrument)
        # P3-00参数 提升机的设备ID
        p3_00 = instrument.read_register(0x0300)
        mainUI.textBrowser.append(f"p3-00 = {hex(p3_00)}")
        # P3-01参数 提升机的波特率
        p3_01 = instrument.read_register(0x0302)
        mainUI.textBrowser.append(f"p3-01 = {hex(p3_01)}")
        # P3-09参数 同步设置
        p3_09 = instrument.read_register(0x0312)
        mainUI.textBrowser.append(f"p3-09 = {hex(p3_09)}")
        instrument.serial.close()
    except Exception:
        mainUI.textBrowser.append("参数读取失败，请重试,请排查串口是否错误！")
        mainUI.textBrowser.moveCursor(QtGui.QTextCursor.End)
        traceback.print_exc()

#该函数用于读取提升机p2-10～p2-17参数
def readP2_10toP2_17Argu(instrument):
        # P2-10参数 备注DI1
        p2_10 = instrument.read_register(0x0214)
        mainUI.textBrowser.append(f"p2-10 = {hex(p2_10)}")
        # P2-11参数 备注DI2
        p2_11 = instrument.read_register(0x0216)
        mainUI.textBrowser.append(f"p2-11 = {hex(p2_11)}")
        # P2-12参数 备注DI3
        p2_12 =instrument.read_register(0x0218)
        mainUI.textBrowser.append(f"p2-12 = {hex(p2_12)}")
        # P2-13参数 备注DI4
        p2_13 =instrument.read_register(0x021A)
        mainUI.textBrowser.append(f"p2-13 = {hex(p2_13)}")
        # P2-14参数 备注DI5
        p2_14 = instrument.read_register(0x021C)
        mainUI.textBrowser.append(f"p2-14 = {hex(p2_14)}")
        # P2-15参数 备注DI6
        p2_15 = instrument.read_register(0x021E)
        mainUI.textBrowser.append(f"p2-15 = {hex(p2_15)}")
        # P2-16参数 备注DI7
        p2_16 = instrument.read_register(0x0220)
        mainUI.textBrowser.append(f"p2-16 = {hex(p2_16)}")
        # P2-17参数 备注DI8只用于加保护传感器 默认值0x21，测试值0
        p2_17 = instrument.read_register(0x0222)
        mainUI.textBrowser.append(f"p2-17 = {hex(p2_17)}")


#初始化Canopen socket
def initCanInterface(portNumber,baud):
    mainUI.textBrowser.append("初始化CanOpen接口")  
    network = canopen.Network()
    network.connect(bustype='slcan', channel=portNumber, bitrate=baud)
    mainUI.textBrowser.append("CanOpen接口初始化完成")
    return network

#控制驱动器，使电机按照位置模式运行。
#A2驱动器canopen通信协议控制，参考台达A2CANOpen英文文档中profile position mode一节
def testPositionMode(portNumber):
    try:
        mainUI.textBrowser.append("开始测试提升机电机运转")
        network = initCanInterface(portNumber,Baud)
        deltaMotorNode = network.add_node(NodeID, './ASDA-A3_v04.eds')
        deltaMotorNode.nmt.state = 'OPERATIONAL'
        deltaMotorNode.sdo[0x6060].write(0x01)
        deltaMotorNode.sdo[0x607A].write(100000000)
        deltaMotorNode.sdo[0x6081].write(5000000)
        deltaMotorNode.sdo[0x6083].write(300)
        deltaMotorNode.sdo[0x6084].write(300)
        #stateWords operation to enable servermotor
        deltaMotorNode.sdo[0x6040].write(0x06)
        deltaMotorNode.sdo[0x6040].write(0x07)
        deltaMotorNode.sdo[0x6040].write(0x0F)
        deltaMotorNode.sdo[0x6040].write(0x7F)
        #check current position of The motor（The unit is PPU）
        current_position =  deltaMotorNode.sdo[0x6064].read()
        mainUI.textBrowser.append(f"电机当前位置为:{current_position}PPU")
        #check current running state of The motor
        # the specific meaning of state code refere to delta documentation
        current_status =  deltaMotorNode.sdo[0x6041].read()
        mainUI.textBrowser.append(f"当前电机运转状态码:{current_status}")
        mainUI.textBrowser.append("提升机测试运转成功")
        network.disconnect()
    except Exception:
        mainUI.textBrowser.append("提升机测试失败，请检查以下几点")
        mainUI.textBrowser.append("1：驱动器参数是否选择正确，2：驱动器配置完成是否重启，3：canopen连线是否正确")


def findDevice(baud):
    global NodeID
    isFindDevice = False
    network = initCanInterface(PortNumber,baud)
    network.nmt.send_command(0x01)
    # This will attempt to read an SDO from nodes 1 - 127
    numbers = list(range(1, 128))
    random.shuffle(numbers)
    sdo_req = b"\x40\x00\x10\x00\x00\x00\x00\x00"
    for node_id in numbers:
        network.send_message(0x600 + node_id, sdo_req)
    # We may need to wait a short while here to allow all nodes to respond
    time.sleep(0.05)
    for node_id in network.scanner.nodes:
        NodeID = node_id
        mainUI.textBrowser.append(f"节点ID的为{node_id},16进制表示为{hex(node_id)}")
        isFindDevice = True
    network.disconnect()
    return isFindDevice

def searchBaud():
    global Baud
    mainUI.textBrowser.append("开始检测波特率")
    isFindDevice = False
    while (isFindDevice == False):
        baudList = [125000, 500000, 750000, 1000000, 250000]
        random.shuffle(baudList)
        for baud in baudList:
            isFindDevice = findDevice(baud)
            if (isFindDevice == True):
                if (baud == 125000):
                    Baud = baud
                    mainUI.textBrowser.append(f"波特率为125000")
                    return
                elif (baud == 250000):
                    Baud = baud
                    mainUI.textBrowser.append(f"波特率为250000")
                    return
                elif (baud == 500000):
                    Baud = baud
                    mainUI.textBrowser.append(f"波特率为500000")
                    return
                elif (baud == 1000000):
                    Baud = baud
                    mainUI.textBrowser.append(f"波特率为1000000")
                    return
                elif (baud == 750000):
                    Baud = baud
                    mainUI.textBrowser.append(f"波特率为750000")
                    return
    mainUI.textBrowser.append("波特率检测完成")

# we use this function to detect Node ID using RS232 based on modbus protocal.
def detectModBusID():
    mainUI.textBrowser.append("开始寻找ModbusNodeID")
    idList = [*range(1,0x7f+1)]
    mainUI.textBrowser.append("请耐心等待")
    mainUI.textBrowser.moveCursor(QtGui.QTextCursor.End)
    random.shuffle(idList)
    for id in idList :
        try:
            # mainUI.textBrowser.append(f"开始尝试id:{id}")
            # modBus协议基本串口参数配置
            instrument = minimalmodbus.Instrument(PortNumber, id)  # port name, slave address (in decimal)
            instrument.serial.baudrate = 38400
            instrument.serial.bytesize = 8
            instrument.serial.stopbits = 2
            instrument.serial.parity = serial.PARITY_NONE
            instrument.mode = minimalmodbus.MODE_RTU
            P3_00 = instrument.read_register(0x0302)
            mainUI.textBrowser.append(f"找到节点：{id}")
            mainUI.textBrowser.moveCursor(QtGui.QTextCursor.End)
            instrument.serial.close()
            return id
        except Exception:
            instrument.serial.close()
            continue
    mainUI.textBrowser.append("检测失败！检查是否串口选择错误，或者连线不牢")
    return None


def checkCurrentConfig():
    try:
        network = initCanInterface(PortNumber, Baud)
        deltaMotorNode = network.add_node(NodeID, './ASDA-A3_v04.eds')
        deltaMotorNode.nmt.state = 'OPERATIONAL'
        # docs https://hcrobots.feishu.cn/wiki/wikcnRos1XZ9nR1C5cXYaBgY1zd
        # p1-01 value is 0x010C
        p1_01 = deltaMotorNode.sdo[0x2101].read()
        mainUI.textBrowser.append(f"p1-01 = {hex(p1_01)}")
        # p1-42 value is 0
        p1_42 = deltaMotorNode.sdo[0x212A].read()
        mainUI.textBrowser.append(f"p1-42 = {hex(p1_42)}")
        # p1-43 value is 0
        p1_43 = deltaMotorNode.sdo[0x212B].read()
        mainUI.textBrowser.append(f"p1-43 = {hex(p1_43)}")
        # p2-10 value is 0124
        p2_10 = deltaMotorNode.sdo[0x220A].read()
        mainUI.textBrowser.append(f"p2-10 = {hex(p2_10)}")
        # p2-11 value is 0
        p2_11 = deltaMotorNode.sdo[0x220B].read()
        mainUI.textBrowser.append(f"p2-11 = {hex(p2_11)}")
        # p2-12 value is 0
        p2_12 = deltaMotorNode.sdo[0x220C].read()
        mainUI.textBrowser.append(f"p2-12 = {hex(p2_12)}")
        # p2-13 value is 0
        p2_13 = deltaMotorNode.sdo[0x220D].read()
        mainUI.textBrowser.append(f"p2-13 = {hex(p2_13)}")
        # p2-14 value is 0
        p2_14 = deltaMotorNode.sdo[0x220E].read()
        mainUI.textBrowser.append(f"p2-14 = {hex(p2_14)}")
        # p2-15 value is 0
        p2_15 =deltaMotorNode.sdo[0x220F].read()
        mainUI.textBrowser.append(f"p2-15 = {hex(p2_15)}")
        # p2-16 value is 0
        p2_16 = deltaMotorNode.sdo[0x2210].read()
        mainUI.textBrowser.append(f"p2-16 = {hex(p2_16)}")
        # p2-17 value is 0021
        p2_17 = deltaMotorNode.sdo[0x2211].read()
        mainUI.textBrowser.append(f"p2-17 = {hex(p2_17)}")
        # p2-18 value is 0
        p2_18 = deltaMotorNode.sdo[0x2212].read()
        mainUI.textBrowser.append(f"p2-18= {hex(p2_18)}")
        # p2-19 value is 0
        p2_19 = deltaMotorNode.sdo[0x2213].read()
        mainUI.textBrowser.append(f"p2-19= {hex(p2_19)}")
        # p2-20 value is 0108
        p2_20 = deltaMotorNode.sdo[0x2214].read()
        mainUI.textBrowser.append(f"p2-20= {hex(p2_20)}")
        # p2-21 value is 0
        p2_21 = deltaMotorNode.sdo[0x2215].read()
        mainUI.textBrowser.append(f"p2-21= {hex(p2_21)}")
        # p2-22 value is 0
        p2_22 = deltaMotorNode.sdo[0x2216].read()
        mainUI.textBrowser.append(f"p2-22= {hex(p2_22)}")
        # p3-00 value is 01(up)
        p3_00 = deltaMotorNode.sdo[0x2300].read()
        mainUI.textBrowser.append(f"p3-00= {hex(p3_00)}")
        # p3-01 value is 0x0103 bitrate == 250000
        p3_01 = deltaMotorNode.sdo[0x2301].read()
        mainUI.textBrowser.append(f"p3-01= {hex(p3_01)}")
        print("read finished!")
        network.disconnect()
    except Exception:
        mainUI.textBrowser.append(f"查看失败请重试")

#####################################################
#                    创建主界面                       #
#####################################################
class MyWindow(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        global mainUI
        global Baud
        global NodeID
        Baud = 250000
        NodeID = 0
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.setFont(QFont('Helvetica Neue'))
        mainUI = self
        # --------------------------------------------------------------------
        # 设置一个串口检测定时器，每隔0.3自动触发refresh方法刷新串口
        self.timer = QTimer(self)  # 实例化一个定时器
        self.timer.timeout.connect(self.refresh)  # 定时器结束后触发refresh
        self.timer.start(300)  # 开启定时器，间隔0.3s
    # --------------------------------------------------------------------
        self.disableButton()

    #####################################################
    #                    UI按钮函数区                     #
    #####################################################

    def changenodeId(self):
        global NodeID
        self.BtnTestLifter.setDisabled(False)
        self.SensorDetectcomboBox.setDisabled(False)
        self.lineEdit.setDisabled(True)
        if self.canopenIdComboBox.currentText() == "1(上升列)":
            NodeID = 0x1
        elif self.canopenIdComboBox.currentText() == "2(下降列)":
            NodeID = 0x2
        else:
            QMessageBox.warning(self,"警告","请选择设备")
            self.SensorDetectcomboBox.setDisabled(True)
        self.textBrowser.append(f"canopenID为{NodeID}")

    def ProtectSensor(self):
        global SensorValue
        self.BtnConfig.setDisabled(False)
        if self.SensorDetectcomboBox.currentText() == "需要":
            SensorValue = 0x21
        elif self.SensorDetectcomboBox.currentText() == "不需要":
            SensorValue = 0x0
        else:
            QMessageBox.warning(self,"警告","请点击需要或者不需要")
            self.textBrowser.clear()
            self.BtnConfig.setDisabled(True)
        self.textBrowser.append(f"传感器参数配置值为{SensorValue}")
    def disableButton(self):
        self.SensorDetectcomboBox.setDisabled(True)
        self.BtnConfig.setDisabled(True)
        self.BtnTestLifter.setDisabled(True)
        self.BtnBaudDetect.setDisabled(True)
        self.BtnCheckConfig.setDisabled(True)

    def detectBaud(self):
        searchBaud()
        self.BtnTestLifter.setDisabled(False)

    def configDriver(self):
        self.configThread = configDeltaMotorThread()
        self.configThread.started.connect(self.disbleConfigBtn)
        self.configThread.finished.connect(self.enbleConfigBtn)
        self.configThread.start()
    def disbleConfigBtn(self):
        self.BtnConfig.setDisabled(True)
    def enbleConfigBtn(self):
        self.BtnConfig.setDisabled(False)

    def testLifter(self):
        testPositionMode(PortNumber)

    def checkConfig(self):
        self.textBrowser.append(f"开始检测配置值")
        self.textBrowser.append(f"------------------------")
        checkCurrentConfig()
        self.textBrowser.append(f"------------------------")

    def inputRotationValue(self):
        global RotationValue
        try:
            RotationValue = int(self.lineEdit.text())
        except Exception:
            mainUI.textBrowser.append("错误，请输入数字")
        print(RotationValue)
     #--------------------------------------------------------
    #创建一个新线程来查看驱动器配置
    def checkConfigModbus(self):
        self.CheckconfigThread = CheckConfigModbusThread()
        self.CheckconfigThread.started.connect(self.disbleCheckBtn)
        self.CheckconfigThread.finished.connect(self.enbleCheckBtn)
        self.CheckconfigThread.start()
    def disbleCheckBtn(self):
        self.BtnCheckConfigModbus.setDisabled(True)
    def enbleCheckBtn(self):
        self.BtnCheckConfigModbus.setDisabled(False)
     #----------------------------------------------------------

    #--------------------------------------------------------
    #创建一个新线程来检测节点id
    def nodeIdDetectionModbus(self):
        self.idDetetctThread = NodeIdDetetctThread()
        self.idDetetctThread.started.connect(self.disbleIDBtn)
        self.idDetetctThread.finished.connect(self.enbleIDBtn)
        self.idDetetctThread.start()
    def disbleIDBtn(self):
        self.BtnNodeIdDetectionModbus.setDisabled(True)
    def enbleIDBtn(self):
        self.BtnNodeIdDetectionModbus.setDisabled(False)
    #----------------------------------------------------------

    # --------------------------------------------------------
    # 创建一个新线程来配置举升机
    def configLifter(self):
        self.configLifterTh = configLifterThread()
        self.configLifterTh.started.connect(self.disableConfigLifterBtn)
        self.configLifterTh.finished.connect(self.enableConfigLifterBtn)
        self.configLifterTh.start()
    def disableConfigLifterBtn(self):
        self.BtnConfigLifter.setDisabled(True)
    def enableConfigLifterBtn(self):
        self.BtnConfigLifter.setDisabled(False)
    # ----------------------------------------------------------

    # --------------------------------------------------------
    # 创建一个新线程来读取举升机配置
    def readLifterConfig(self):
        self.checkLifterconfig = CheckLifterConfigThread()
        self.checkLifterconfig.started.connect(self.disableCheckLifterconfigBtn)
        self.checkLifterconfig.finished.connect(self.enableCheckLifterconfigBtn)
        self.checkLifterconfig.start()

    def disableCheckLifterconfigBtn(self):
        self.BtnCheckLifterConfig.setDisabled(True)

    def enableCheckLifterconfigBtn(self):
        self.BtnCheckLifterConfig.setDisabled(False)


    def refresh(self):
        global num_last
        global PortNumber
        port_list = get_port_list()
        num = len(port_list)
        if (num < num_last):
            num_last = num
            QMessageBox.information(self, "提示", "检测到USB调试线被拔出，请确认当前调试线是否正确")
            PortNumber = port_list[-1][0]
            self.textBrowser.setPlainText(f"自动设置当前调试串口为为{PortNumber},请确认当前调试线！")
        if (num > num_last):
            num_last = num
            QMessageBox.information(self, "提示", "检测到有有新的USB调试线插入")
            PortNumber = port_list[-1][0]
            self.textBrowser.setPlainText(f"已检测到调试线，调试线为{PortNumber},请开始配置吧！")

    # ----------------------------------------------------------



if __name__ == "__main__":
    global PortNumber
    global num_last
    portList = get_port_list()
    num_last = len(portList)
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    #获取该串口的厂商参数
    port = portList[-1][1]
    if ("usb" not in port.lower() and "can" not in port.lower()) or num_last == 0 :
        BtnInfo = QMessageBox.information(myWin, "提示", "请先插入调试线,开启测试")
        if BtnInfo == 1024:
            portList = get_port_list()
            num_last = len(portList)
            PortNumber = portList[-1][0]  # 获取该串口的串口名
            myWin.textBrowser.append(f"已检测到调试线，调试线为{PortNumber},请开始配置吧！")

    else:
        PortNumber = portList[-1][0] #获取该串口的串口名
        myWin.textBrowser.append(f"已检测到调试线，调试线为{PortNumber},请开始配置吧！")
    sys.exit(app.exec_())


