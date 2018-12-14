#coding=utf-8
from PyQt5.QtCore import QThread, pyqtSignal,Qt
from PyQt5 import QtWidgets
from PyQt5.QtNetwork import QAbstractSocket,QHostAddress, QTcpServer, QTcpSocket,QNetworkRequest
from exts import getip,register_company,updateip_webserver
import time
from DataQueryServer import DataQueryTcpServer
import socketserver
class MyProgressBar(QtWidgets.QProgressBar):
    def __init__(self):
        super(MyProgressBar,self).__init__()
        self.setTextVisible(False)
        self.setFormat('%v')
        self.setRange(0,10)
        self.setMinimumWidth(480)

class ProgressDialog(QtWidgets.QProgressDialog):
    def __init__(self,parent):
        super(ProgressDialog,self).__init__(parent)
        self.setWindowTitle(u'请稍等')
        self.setMinimumWidth(510)
        # 指定为模态窗口，禁止父窗口输入
        myb = MyProgressBar()
        self.setBar(myb)
        self.setCancelButton(None)
        # self.setWindowFlags(Qt.WindowContextHelpButtonHint)
        self.setWindowModality(Qt.WindowModal)


        self.show()

class ProgressThread(QThread):
    updatevalue = pyqtSignal(int)
    def __init__(self):
        super(ProgressThread, self).__init__()
        self._stop_flag = False

    def run(self):
        _i = 1
        while not self._stop_flag:
            _i += 1
            if _i >=100:
                _i = 1
            self.updatevalue.emit(_i)
            time.sleep(0.1)

    def stop(self):
        self._stop_flag = True

class GetIPThread(QThread):
    getipsignal = pyqtSignal(dict)
    def __init__(self, parent = None):
        super(GetIPThread,self).__init__(parent)
        
    def run(self):
        _ip = getip()
        self.getipsignal.emit(_ip)

    def stop(self):
        self.terminate()

class RegisterThread(QThread):
    ressignal = pyqtSignal(dict)
    def __init__(self,keydog,name,ip,parent=None):
        super(RegisterThread,self).__init__(parent)
        self._keydog= keydog
        self._name = name
        self._ip = ip

    def run(self):
        try:
            self.ressignal.emit( register_company(self._keydog,self._name,self._ip))
        except Exception as e:
            _errmsg = {
                'code':'-1',
                'msg':'DQThreads.UpdateIPOnWebServer Error %s' % e
                }
            self.ressignal.emit(_errmsg)


    def stop(self):
        self.terminate()

class UpdateIPOnWebServer(QThread):
    updateip_signal = pyqtSignal(dict)
    def __init__(self,keydog,ip,parent=None):
        super(UpdateIPOnWebServer,self).__init__(parent)
        self._keydog = keydog
        self._ip = ip

    def run(self):
        try:
            self.updateip_signal.emit(updateip_webserver(self._keydog,self._ip))
        except Exception as e:
            _errmsg = {
                'code':'-1',
                'msg':'DQThreads.UpdateIPOnWebServer Error %s' % e
                }
            self.updateip_signal.emit(_errmsg)


    def stop(self):
        self.terminate()

#class WebServer(QThread):
#    webservermsg_signal =pyqtSignal(str)
#    def __init__(self,parent = None):
#        super(WebServer,self).__init__(parent)

#    def run(self):
#        try:
                       
#            self.srv = DataQueryTcpServer()
#            self.srv.listen(QHostAddress('0.0.0.0'),1509)
#            self.srv.sendMessageToMain_signal.connect(self.emit_webservermsg_signal)
#            self.emit_webservermsg_signal(u'启动服务...')

#        except Exception as e:
#            _errmsg= {
#                'code':'-1',
#                'msg':'DQThreads.WebServer Error %s' % e
#                }
#            self.webservermsg_signal.emit(_errmsg['msg'])
    
#    def emit_webservermsg_signal(self,msg):
#        print(msg)
#        _msg = str(msg)
#        self.webservermsg_signal.emit(_msg)

#    def stop(self):
#        self.emit_webservermsg_signal(u'停止服务...')
#        self.terminate()

