#!/usr/bin/env Python
# coding:utf-8
""""
爬取http://www.52psy.cn 的心理咨询机构
@author: hz
"""
import requests
import os
import string
import numpy as np
import pandas as pd
import time
from urllib.parse import quote
import re
from bs4 import BeautifulSoup
from selenium import webdriver

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}



provinces = ['jiangsu/', 'zhejiang/', 'anhui/','guangdong/', 'guangxi/', 'shanghai/',
             'jiangxi/', 'fujian/', 'shandong/', 'shanxi/', 'hebei/', 'henan/',
             'tianjin/', 'liaoning/', 'heilongjiang/', 'jilin/', 'hubei/', 'hunan/',
             'sichuan/', 'chongqing/', 'shanxis/', 'gansu/', 'yunnan/', 'xinjiang/',
             'neimeng/', 'hainan/', 'guizhou/', 'gansu/', 'ningxia/']


def save_excel(data, name):
    data_F = pd.DataFrame(data)
    str_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    pd.DataFrame.to_excel(data_F, 'D:\\workdata\\'+str_time+name+'.xls')
    pd.DataFrame.to_csv(data_F, 'D:\\workdata\\'+name+'.csv')

def is_file_exist(name):
    return os.path.exists('D:\\workdata\\'+name+'.csv')

def read_file(name):
    resu = pd.read_csv('D:\\workdata\\'+name+'.csv', index_col=None, encoding='utf-8')
    return resu
def get_html(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except:
        return None

def re_with_html(html,pri):
    str_re = '/it\d/'+pri+'\d{6}/'
    #print(str_re)
    pattern = re.compile('.*?<a href="('+str_re+').*?'
                         , re.S)
    results = re.findall(pattern, str(html))
    return results

def re_with_href(strs):
    pattern = re.compile('.*?<a href="(.*?)">(.*?)</a>.*?', re.S)
    res = re.findall(pattern, str(strs))
    return res

if __name__ == "__main__":
    i = 0
    #results = ['/it2/guangdong/440100/', '/it3/guangdong/440100/']
    #ress = ['http://gzlz.52psy.cn', 'http://gzmdl.52psy.cn']
    results = []
    ress = []
    resss = []
    if is_file_exist('province'):
        resul = read_file('province')
        results = list(resul['0'])
    else:
        for province in provinces:
            url = 'http://www.52psy.cn/instition/'
            i += 1
            url = url + province
            print(url)
            html = get_html(url)
            result = re_with_html(html, province)
            results.extend(result)
            print(i)
        save_excel(results, 'province')
    i = 0
    if is_file_exist('zxs_url'):
        resul = read_file('zxs_url')
        ress = list(resul['0'])
    else:
        for res in results:
            i += 1
            url_x = 'http://www.52psy.cn' + res
            html = get_html(url_x)
            Soup1 = BeautifulSoup(html, 'lxml')
            result = Soup1.select('.kind_1 .kind_2-1 li a')
            ress.extend(result)
            print(i)
        save_excel(ress, 'zxs_url')
    i = 0
    for res in ress:
        res_a = []

        #url_a = res['href']
        re_u = re_with_href(res)
        url_a = re_u[0][0]
        if len(url_a) > 18:
            html = get_html(url_a)
            if html == None :
                continue
            i += 1
            print(i)
            Soup1 = BeautifulSoup(html, 'lxml')
            zxzn = Soup1.select('.brief ul .f1 span')[0].text
            if zxzn == '暂时未添加该信息':
                zxzn_href = ''
            else:
                zxzn_href = 'http://www.52psy.cn'+Soup1.select('.brief ul .f1 span a')[0]['href']
            dz = Soup1.select('.brief ul .f2 span')[0].text
            phone = Soup1.select('.brief ul .f4 span')[0].text
            zxrs = Soup1.select('.brief ul .f5 font span')[0].text
            ktsj = Soup1.select('.brief ul .f6 span')[0].text
            res_a.append(re_u[0][1])  # 咨询室
            res_a.append(zxzn) #咨询指南
            res_a.append(dz) #地址
            res_a.append(phone)#电话
            res_a.append(zxrs)#咨询人数
            res_a.append(ktsj)#开通时间
            res_a.append(zxzn_href)#咨询室简介href
            res_a.append(res)#咨询室href
            if len(resss) == 0:
                resss = res_a
            else:
                resss = np.vstack((resss, res_a))
            if i % 500 == 0:
                save_excel(resss, 'data_'+str(i/1000)+'_')
                resss = []


    print('finish')
    # save_info(results)
