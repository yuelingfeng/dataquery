#coding = utf-8
from PyQt5.QtCore import QThread, pyqtSignal,Qt,QDataStream,QByteArray
from PyQt5.QtNetwork import QAbstractSocket,QHostAddress, QTcpServer, QTcpSocket,QNetworkRequest
import sys,time
from PyQt5.QtWidgets import QApplication
from exts import http_str_to_dict
from json import dumps

class DataQuerySocket(QTcpSocket):
    sendMessageToThread_signal = pyqtSignal(str)

    sendStopToThread_signal = pyqtSignal(dict)


    def __init__(self,socketId,parnet=None):
        super(DataQuerySocket,self).__init__(parnet)
        self.socketId = socketId
        #信号传给自身的方法处理
        self.readyRead.connect(self.recvClientMessage_SendToThread)

    def recvClientMessage_SendToThread(self):
        '''
        :Description Info:接收来自readyRead的信号，处理数据之后发给Thread
        '''
        while self.state() == QAbstractSocket.ConnectedState:
            _msg_dict={
                'wxid':''
                }
            socketData = self.readAll().data()
            if not socketData:
                return
            socketData = socketData.decode('utf-8')
            self.sendMessageToThread_signal.emit(socketData)

    def recvThreadMessage_SentToClient(self,dict):
        try:
            _msg = bytes(dumps(dict),encoding='utf-8')
            self.write(_msg)
            self.sendStopToThread_signal.emit({'code':'0','msg':u'消息发送成功！'})
        except Exception as e:
            self.sendStopToThread_signal.emit({'code':'-1','msg':str(e)})

class ServerThread(QThread):
    
    sendMessageToServer_signal = pyqtSignal(dict)

    sendMessageToSocket_signal = pyqtSignal(dict)

    def __init__(self,socketid, parent = None):
        super(ServerThread,self).__init__(parent)
        self.socketId = socketid


    def run(self):
        '''
        :Description Info:线程内开启一个TcpSocket服务，用于接收来自Client的数据

        '''
        dqs = DataQuerySocket(self.socketId)
        if not dqs.setSocketDescriptor(self.socketId):
            return
        dqs.sendMessageToThread_signal.connect(self.recvMessageFromSocket)
        dqs.sendStopToThread_signal.connect(self.sendMessageToServer)
        self.sendMessageToSocket_signal.connect(dqs.recvThreadMessage_SentToClient)
        self.exec_()

    def recvMessageFromSocket(self,str):
        '''
        :Description Info:接收来自Socket的信号
        '''
        _str = str.split(' ')
        if len(_str[1]) == 1:
            _dict = {'code':'-1','msg':u'参数错误！'}
            self.snendMessageTocket_signal.emit(_dict)
            self.sendMessageToServer_signal.emit(_dict)
        else:
            _dict = http_str_to_dict(_str)

            self.sendMessageToServer_signal.emit(_dict)

    def sendMessageToSocket(self,msg):
        self.sendMessageToSocket_signal.emit(msg)

    def sendMessageToServer(self,dict):
        self.stoped()

    def stoped(self):
        #self.terminate()
        self.sendMessageToServer_signal.emit({'code':'0','msg':'Stop thread'})
        self.quit()
        self.wait()
        self.finished.emit()


class DataQueryTcpServer(QTcpServer):

    sendMessageToThread_signal = pyqtSignal(dict)

    sendMessageToMain_signal = pyqtSignal(dict)


    def __init__(self,parent=None):
        super(DataQueryTcpServer,self).__init__(parent)

    def incomingConnection(self,socketid):
        '''
        :description Info:内置方法，监听到有client连接时自动触发
                               开启一个线程
         '''
        st = ServerThread(socketid,self)
        st.sendMessageToServer_signal.connect(self.recvMessageFromThread)
        self.sendMessageToThread_signal.connect(st.sendMessageToSocket)
        st.finished.connect(st.deleteLater)
        self.sendMessageToMain_signal.emit({'code':'0','msg':'Start thread'})
        st.start()
        

    def recvMessageFromThread(self,dict):
        self.sendMessageToMain_signal.emit(dict)

    def sendMessageToThread(self,msg):
        self.sendMessageToThread_signal.emit(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sqts = DataQueryTcpServer()
    sqts.listen(QHostAddress('0.0.0.0'),1509)
    sys.exit(app.exec_())
    
 
