# -*- coding: utf-8 -*-

from json import load
import urllib
from urllib.request import urlopen
from PyQt5.QtWidgets import QWidget, QMessageBox

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

_server_url = 'https://sqstudio.com.cn'

def getip():
    try:
        return {'code':'0', 'msg':load(urlopen('http://jsonip.com'))['ip']}
    except Exception as e:
        return { 'code':'-1',
            'msg' : 'exts.resigter_wx error %s' % e
            }

def register_company(keydog,name,ip):
    try:
        _name = urllib.parse.quote(name)
        _url = _server_url + u'/register?sn=%s&name=%s&ipaddress=%s' % (keydog,_name,ip)
        
        _result = urlopen(_url)
        return load(_result)
    except Exception as e:
        return { 'code':'-1',
            'msg' : 'exts.resigter_wx error %s' % e
            }
def updateip_webserver(keydog,ip):
    try:
        _url  = _server_url+ u'/updateip?sn=%s&ipaddress=%s' % (keydog,ip)
        _result = urlopen(_url)
        return load(_result)

    except Exception as e:
        return { 'code':'-1',
            'msg' : 'exits.updateip_webservererror %s' % e
            }

def http_str_to_dict(str):
    '''
    :Description Info:此函数用于把socket接收到的参数转换为dict
    :input type:list
    :output type:dict
    '''
    
    _str = str[1][2:]
    _dict = {}
    for _ele in _str.split('&'):
        _ele_list = _ele.split('=')
        _dict[_ele_list[0]] = _ele_list[1]
    return _dict   