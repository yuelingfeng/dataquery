#coding=utf-8
import os

class DQFile:
    def __init__(self,context=None):
        self.__context= bytes(str(context), encoding = "utf8")
    
    def read(self):
        try:
            with open('D:\python_workspace\MobileManager\pcclient\dataquery\dataquery\dq.conf','rb') as fo:
                return fo.readlines()
        except Exception as e:
            return e

    def write(self):
        try:
            if not self.__context:
                return True
            with open('D:\python_workspace\MobileManager\pcclient\dataquery\dataquery\dq.conf','wb') as fw:
                fw.write(self.__context)
                return True
        except Exception as e:
            return e
