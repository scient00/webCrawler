#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from CrawlerScript.DoubleColorBallLottery import *

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

def runDoubleCB():
    try:
        dball = DoubleColorBall()
        dball.generateXlsReport()

        numberList = dball.getNumberList()
        analyse = DcdAnalyze(numberList)
        analyse.process()
        pass

    except:
        logging.error('runStart error!!!')


