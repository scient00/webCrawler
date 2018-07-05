#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests, bs4,re,xlwt,datetime
import os, time,logging,threading
from BasicMethod.BasicMethod import *
import numpy as np

ThreadLock = threading.Lock()

class DoubleColorBallThread(threading.Thread):
    def __init__(self,threadId,pageList):
        threading.Thread.__init__(self)
        self.__threadId = threadId
        self.__pageList = pageList
        self.__numberList = []

    def run(self):
        try:
            logging.info('Start Thread %d....' % self.__threadId)

            for page_num in self.__pageList:
                url = "http://kaijiang.zhcw.com/zhcw/html/ssq/list_" + str(page_num) + ".html"
                reponse = requests.get(url=url)
                time.sleep(5)
                reponse.encoding = 'utf-8'
                html = reponse.text
                rule = r"<tr>.*?<td align=\"center\">(.*?)</td>.*?<td align=\"center\">(.*?)</td>.*?<td align=\"center\" style=\"padding-left:10px;\">.*?<em class=\"rr\">(.*?)</em>.*?<em class=\"rr\">(.*?)</em>.*?<em class=\"rr\">(.*?)</em>.*?<em class=\"rr\">(.*?)</em>.*?<em class=\"rr\">(.*?)</em>.*?<em class=\"rr\">(.*?)</em>.*?<em>(.*?)</em></td>"
                num = re.findall(rule, html, re.S | re.M)
                ThreadLock.acquire()
                logging.info(" 正在处理第%s页数据......" % (page_num))
                ThreadLock.release()
                self.__numberList.extend(num)

            logging.info('End of the thread[%d]' % self.__threadId)
        except:
            logging.error('start thread error!!!')

    def getNumberList(self):
        try:
            return self.__numberList
        except:
            logging.error('getNumberList error!!!')
            return []

class DoubleColorBall(object):
    def __init__(self):
        self.__url = "http://kaijiang.zhcw.com/zhcw/html/ssq/list_1.html"
        self.__all_page = self.__getAllPage()
        self.__indexName = ['日期','期数','第一个红球','第二个红球','第三个红球','第四个红球','第五个红球','第六个红球','蓝球']
        self.__threadNum = 30
        self.__numberList = self.__getNumber()

    def __getAllPage(self):
        try:
            reponse = requests.get(url=self.__url)
            reponse.encoding = 'utf-8'
            html = reponse.text
            all_page = int(re.findall(r"class=\"pg\".*?<strong>(.*?)</strong>", html)[0])
            return all_page
        except:
            logging.error('__getAllPage error!!!')
            return 0

    def __partitionPage(self):
        try:
            out = []
            num = int(self.__all_page/self.__threadNum)
            rem = int(self.__all_page%self.__threadNum)
            for k in range(0,self.__threadNum):
                outTemp = []
                for z in range(0,num):
                    outTemp.append(k*num + z + 1 )

                out.append(outTemp)
                if k==self.__threadNum-1:
                    for x in range(0,rem):
                        out[x].append(num*self.__threadNum + x + 1)

            return out
        except:
            logging.error('__partitionPage error!!!')
            return []

    def __getNumber(self):
        try:
            numberList = []
            threadList = []
            startTime = datetime.datetime.now()
            processPage = self.__partitionPage()

            for k in range(0,self.__threadNum):
                numberThreadInput = DoubleColorBallThread(k+1,processPage[k])
                numberThreadInput.start()
                threadList.append(numberThreadInput)

            # 等待所有进程或线程结束
            for end in threadList:
                end.join()
                numberList.extend(end.getNumberList())

            endTime = datetime.datetime.now()
            multiTotalTime = float((endTime - startTime).total_seconds() * 1000)

            print("全部数据处理完成", '总耗时：%f' % multiTotalTime + 'ms')
            numberList.sort()
            return numberList

        except:
            logging.error('__getNumber error!!!')
            return []

    def generateXlsReport(self,xmlpath ='getData'):
        try:
            CreateFolder(xmlpath)
            nSize = -1
            fxml = xlwt.Workbook(encoding='utf-8')
            sheet01 = fxml.add_sheet(u'双色球', cell_overwrite_ok=True)
            for z,name in enumerate(self.__indexName):
                sheet01.write(0,z,name)

            for num in self.__numberList:
                nSize += 1
                for i in range(len(num)):
                    sheet01.write(nSize + 1, i, num[i])
            fxml.save(u"getData/doubleColorBallResult.xls")

        except:
            logging.error('generateXlsReport error!!!')

    def getNumberList(self):
        try:
            numberList = self.__numberList
            del numberList[0]
            return numberList
        except:
            logging.error('getNumberList error!!!')
            return []

class DcdAnalyze(object):
    def __init__(self,numberList = []):
        self.__numberList = numberList
        self.__readList = [e for e in range(1,34)]
        self.__blueList = [e for e in range(1,17)]
        self.__label = ['red1','red2','red3','red4','red5','red6','blue']
        self.__dcd_count_dict = self.__createDict(0)
        self.__dcd_pro_dict = self.__createDict(0.0)

    def __createDict(self,value = None):
        try:
            dcd_pro_dict = {}
            for label in self.__label:
                red_count_dict = {}
                blue_count_dict = {}
                if label.find('blue') != -1:
                    for k in self.__blueList:
                        blue_count_dict[k] = value
                        dcd_pro_dict[label] = blue_count_dict
                else:
                    for k in self.__readList:
                        red_count_dict[k] = value
                    dcd_pro_dict[label] = red_count_dict


            return dcd_pro_dict
        except:
            logging.error('__createDict error!!!')

    def process(self):
        try:
            for num in self.__numberList:
                for z,label in enumerate(self.__label):
                    self.__dcd_count_dict[label][int(num[2 +z])] += 1

            for dcdname in self.__label:
                if dcdname.find('blue') != -1:
                    for number in self.__blueList:
                        self.__dcd_pro_dict[dcdname][number] = 1.0 * self.__dcd_count_dict[dcdname][number] / len(
                            self.__numberList)
                else:
                    for number in self.__readList:
                        self.__dcd_pro_dict[dcdname][number] = 1.0*self.__dcd_count_dict[dcdname][number]/len(self.__numberList)


        except:
            logging.error('process error!!!')





