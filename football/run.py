#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: aaron
# @File: run.py
# @Time: 2017/12/7 18:13
# @Contact: liuzhongxian@jinuo.me
# @Description: demo

from scrapy import cmdline

#name = 'team'
name = 'game'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())