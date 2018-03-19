#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: aaron
# @File: dbhelper.py
# @Time: 2018/2/24 13:35
# @Contact: liuzhongxian@jinuo.me
# @Description: demo

import db
import config

db.create_engine(config.MYSQL_USER, config.MYSQL_PASSWD, config.MYSQL_DBNAME)

def select_race_all():
    sql = 'select * from race'
    data = db.select(sql)
    return data

def select_team_id(*args):
    sql = 'select rid from team where teamId = ?'
    data = db.select_id(sql, *args)
    return data

def select_team():
    sql = 'select * from team'
    data = db.select(sql)
    return data

def insert(table, **kwargs):
    db.insert(table, **kwargs)

def select_match_id(*args):
    sql = 'select * from game where matchId = ?'
    data = db.select_id(sql, *args)
    return data

def update_insert_team(table, items):
    data = db.insert_one_update(table, items)
    return data

def update_insert_game(table, items):
    data = db.insert_one_update(table, items);
    return data