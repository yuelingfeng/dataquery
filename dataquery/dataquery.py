# -*- coding: utf-8 -*-

from PyQt5 import QtGui,QtCore
from PyQt5.QtWidgets import QWidget, QMessageBox
from dataquery_form import Ui_Form
from PyQt5.QtNetwork import QHostAddress
from DQFile import DQFile
from DQThreads import GetIPThread,RegisterThread,UpdateIPOnWebServer
from DataQueryServer import DataQueryTcpServer
from datetime import datetime
from json import dumps,loads

class DataQuery(QWidget):
    __web_state = 0
    def __init__(self, parent=None):
        super(DataQuery, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.updateip()
        self.ui.lineEdit_IPAddress.setEnabled(False)
        self.readconfig()
        
        
        
    def __server(self):
        self.srv = DataQueryTcpServer()
        self.srv.listen(QHostAddress('0.0.0.0'),1509)
        self.srv.sendMessageToMain_signal.connect(self.server_work)
        self.logstr(u'启动服务...')
        self.__web_state = 1

    def server_work(self,msg):
        try:
            self.logstr(msg.get('msg'))
            self.srv.sendMessageToThread(msg)
            self.logstr(u'返回结果：%s' % msg)
        except Exception as e:
            self.logstr('DataQuery.server_work error: %s' % e)
        
    def updateip_data(self,ip):
        if ip.get('code') == '0':
            self.ui.lineEdit_IPAddress.setText(ip['msg'])
            self.getipthread.stop()
            self.ui.pushButton_register.setEnabled(True)
            self.ui.pushButton_update.setEnabled(True)
            self.logstr('外网IP获取完成')
            self.updateip_webserver()
        else:
            self.getipthread.stop()
            self.logstr(u'获取外网IP地址失败,请检查网络是否正常!')
            self.ui.pushButton_update.setEnabled(True)

    def updateip_webserver(self):
        if not self.ui.lineEdit_KeyDog.text():
            self.logstr('加密狗ID不存在，未能把外网IP更新到服务器！检查加密狗号后点击[更新]按钮进行手动更新！')
            return
        self.logstr('连接web服务器,并更新IP地址')
        _ip = self.ui.lineEdit_IPAddress.text()+':'+self.ui.lineEdit_Port.text()
        _keydog = self.ui.lineEdit_KeyDog.text()
        self.uiws = UpdateIPOnWebServer(_keydog,_ip)
        self.uiws.updateip_signal.connect(self.updatewebipres)
        self.uiws.start()

    def updatewebipres(self,msg):
        if msg['code'] == '0':
            self.logstr('更新成功')
            self.__server()
        else:
            self.logstr(msg['msg'])
        self.uiws.stop()
        

    def updateip(self):
        if self.__web_state == 1:
            self.srv.stop()
            self.__web_state = 0
        self.getipthread = GetIPThread()
        self.ui.lineEdit_IPAddress.setText('正在获取IP')
        self.logstr('开始获取外网IP地址...')
        self.ui.pushButton_register.setEnabled(False)
        self.ui.pushButton_update.setEnabled(False)
        self.getipthread.getipsignal.connect(self.updateip_data)
        self.getipthread.start()

    def register(self):
        _ip = self.ui.lineEdit_IPAddress.text()+':'+self.ui.lineEdit_Port.text()
        _name = self.ui.lineEdit_CompanyName.text()
        _keydog = self.ui.lineEdit_KeyDog.text()
        self.rt = RegisterThread(_keydog,_name,_ip)
        self.rt.ressignal.connect(self.register_res)
        self.rt.start()

    def register_res(self,msg):
        if msg['code'] =='0':
            QMessageBox.information(self,"注册提示","注册成功！")

        else:
            QMessageBox.information(self,"注册提示",msg['msg'])
        self.rt.stop()

    def saveset(self):
        _servername = self.ui.lineEdit_ServerName.text()
        _database = self.ui.lineEdit_DataBase.text()
        _loginid = self.ui.lineEdit_LoginID.text()
        _loginpwd = self.ui.lineEdit_LoginPwd.text()
        _companyname = self.ui.lineEdit_CompanyName.text()
        _keydog = self.ui.lineEdit_KeyDog.text()
        _port = self.ui.lineEdit_Port.text()

        if not _servername:
            QMessageBox.information(self,"输入有误","服务器名称必须填写！")
            return
        if not _database:
            QMessageBox.information(self,"输入有误","数据库名称必须填写！")
            return
        if not _loginid:
            QMessageBox.information(self,"输入有误","用户名称必须填写！")
            return
        if not _loginpwd:
            QMessageBox.information(self,"输入有误","用户密码必须填写！")
            return
        if not _companyname:
            QMessageBox.information(self,"输入有误","公司名称必须填写！")
            return
        if not _keydog:
            QMessageBox.information(self,"输入有误","加密狗号必须填写！")
            return
        if not _port:
            QMessageBox.information(self,"输入有误","加密狗号必须填写！")
            return


        _dict_set = {'servername':'%s' % _servername,'database':'%s' % _database, \
            'loginid':'%s' % _loginid,'loginpwd':'%s' % _loginpwd,'companyname':'%s' % _companyname,'keydog':'%s' % _keydog,'port':'%s' % _port}
        _writeres = DQFile(dumps(_dict_set)).write()
        if _writeres == True:
            QMessageBox.information(self,u"提示",u"保存成功！")
        else:
            QMessageBox.information(self,u"提示",str(_writeres))


    def logstr(self,msg):
        _msg= str(msg)
        _logmsg = self.ui.textEdit_log.toPlainText() + str(datetime.now())+":"+_msg+'\n'
        self.ui.textEdit_log.setText(_logmsg)

    def readconfig(self):
        _config = DQFile().read()[0].decode('utf-8')

        _configs = loads(_config)
        self.ui.lineEdit_ServerName.setText(_configs.get('servername'))
        self.ui.lineEdit_DataBase.setText(_configs.get('database'))
        self.ui.lineEdit_LoginID.setText(_configs.get('loginid'))
        self.ui.lineEdit_LoginPwd.setText(_configs.get('loginpwd'))
        self.ui.lineEdit_CompanyName.setText(_configs.get('companyname'))
        self.ui.lineEdit_KeyDog.setText(_configs.get('keydog'))
        self.ui.lineEdit_Port.setText(_configs.get('prot','1508'))
