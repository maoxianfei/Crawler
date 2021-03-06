#!/usr/bin/env python
# encoding: utf-8
'''
多线程
from multiprocessing import Pool
pool=Pool()
pool.map(downloadimg,id_list)#传入的是函数本身，不用downloadimg（）
代理IP
import random
proxy_list = [
            'http:110.110.110.110',
            'http:110.110.110.110',
        ]
proxy_ip = random.choice(proxy_list)
proxies = {'http': proxy_ip}
webdata=requests.get(url,proxies=proxies)
功能：下载花瓣网图片，根据用户输入页数。支持单线程和多线程，支持代理IP下载
思路：每次朝favorite/beauty网页请求100个数据，返回图片的ID和key值，存储在本地文件。通过读取txt文件从而实现了可以调取多线程方法。
原来的方法是解析网页每个id得到链接开始下载，下载完后再继续下一个链接解析下载。
核心：每次当前网页解析完成后取列表中最后一个id用来构造下一次的访问网页，下载重复的概率比较低，并没有对列表存储的链接去重。
限制：花瓣网似乎对爬虫限制较严格，单线程每次下载需等待两秒，多线程很容易被封。代理IP不稳定。
'''
import re
import requests
import time
import os
import urllib.request
from multiprocessing import Pool
import random
def createFile():
    global path
    filetime = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
    path = './flower_beauty/' + filetime
    #创建 flower_beauty 文件夹
    if not os.path.exists('./flower_beauty'):
        os.mkdir('./flower_beauty')
    #创建 时间戳文件夹和链接缓存文本
    if not os.path.exists(path):
        os.mkdir(path)
    return path
#图片下载，需要key值，构造链接
def downloadimg(key):
    global path
    imgurl='https://hbimg.b0.upaiyun.com/'+str(key)+'_fw658'
    urllib.request.urlretrieve(imgurl,path+'/'+str(key)+'.jpg')
#字符串优化，待用
def validname(title):
    rstr='[\(\)\'\\\]'
    valid_title=re.sub(rstr,'',title)
    return valid_title
#解析图片链接函数
def save(limit):#save id to local txt
    createFile()
    print("创建文件成功")
    page= 0
    url = 'https://huaban.com/favorite/beauty/'
    print('正在解析网页')
    while page<limit:
        page+=1
        print('解析第{}页'.format(page))
        time.sleep(2)#每解析一页等待两秒
        #尝试下载，如果出错可能为请求次数过多导致
        # 代理IP http://cn-proxy.com/
        proxy_list = [
            'http:',
            'http:',
        ]
        proxy_ip = random.choice(proxy_list)
        proxies = {'http': proxy_ip}
        try:
            #普通访问
            webdata=requests.get(url)
            #代理访问
            # webdata=requests.get(url,proxies=proxies)
            #正则匹配id和key
            id_key=re.findall('"pin_id":(\d{9}).*?"key":"(.*?)"',webdata.text)
            f=open(path+'.txt','a')#打开txt文件准备存储数据
            for id in id_key:#遍历数据
                id=str(id[1])#转为字符串来存储，[1]是只截取key，不需要id
                f.write(id)
                f.write('\n')
            f.close()
            next_id=id_key[-1][0]
            url='https://huaban.com/favorite/beauty/?ixvdrhfy&since={}&limit=100&wfl=1'.format(next_id)
        except:
            print('Time out')
#读取图片链接下载函数
def read():
    id_list=[]
    f=open(path+'.txt','r')
    for line in f:
        id_list.append(line[:-1])#每行末尾有换行符，通过截取最后两位去掉
    f.close()
    #多线程下载方法(会封IP，需要添加代理)
    # pool=Pool()
    # pool.map(downloadimg,id_list)
    #单线程下载方法
    for key in id_list:
        global count
        count+=1
        downloadimg(key)
        time.sleep(2)
        print('download at {}'.format(count))
if __name__ == '__main__':
    count=0
    limit=int(input('输入爬取页数（每页大约80个图片）：'))  #页数限制
    save(limit)    #解析图片链接并保存到本地txt文件
    print('解析完成, 文件保存于当前目录')
    read()    #读取链接进行下载
    print('Download success')
