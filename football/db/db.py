#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: aaron
# @File: db.py
# @Time: 2018/2/23 17:48
# @Contact: liuzhongxian@jinuo.me
# @Description: 数据库操作工具
import time
import threading
import functools

engine = None

#引擎对象
class _Engine(object):
    def __init__(self, connect):
        self._connect = connect

    def connect(self):
        return self._connect()

def create_engine(user, password, database, host='127.0.0.1', port=3306, **kw):
    """
    db模型的核心函数，用于连接数据库, 生成全局对象engine，
    engine对象持有数据库连接
    """
    import pymysql
    global engine
    if engine is not None:
        raise Exception()
    params = dict(user=user, password=password, database=database, host=host, port=port)
    defaults = dict(use_unicode=True, charset='utf8', autocommit=False)
    for k, v in defaults.iteritems():
        params[k] = kw.pop(k, v)
    params.update(kw)
    engine = _Engine(lambda: pymysql.connect(**params))

class _LasyConnection(object):
    '''
    惰性连接对象
    仅当需要cursor对象时，才连接数据库，获取连接
    '''

    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            _connection = engine.connect()
            self.connection = _connection
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            _connection = self.connection
            self.connection = None
            _connection.close()

# 持有数据库连接的上下文对象
class _DbCtx(threading.local):
    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return not self.connection is None

    def init(self):
        self.connection = _LasyConnection()
        self.transaction = 0

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()

_db_ctx = _DbCtx()

class _ConnectionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()

def connection():
    return _ConnectionCtx()

def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        with _ConnectionCtx():
            return func(*args, **kwargs)
    return _wrapper

class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions += 1
        return self

    def __enter__(self, exc_type, exec_val, exc_tb):
        global _db_ctx
        _db_ctx.transactions -= 1
        try:
            if _db_ctx.transactions == 0:
                if exc_type is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        try:
            _db_ctx.connection.commit()
        except:
            -_db_ctx.connection.rollback()
            raise

    def rollback(self):
        global _db_ctx
        _db_ctx.connection.rollback()

def transaction():
    return _TransactionCtx()

def _profiling(start, sql=''):
    t = time.time() - start
    pass

def with_transaction(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = time.time()
        with _TransactionCtx():
            func(*args, **kwargs)
        _profiling(start)
    return _wrapper

@with_connection
def _update(sql, *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        r = cursor.rowcount
        if _db_ctx.transactions == 0:
            _db_ctx.connection.commit()
        return r
    except Exception as error:
        print error
    finally:
        if cursor:
            cursor.close()

def update(sql, *args):
    return _update(sql, *args)

class Dict(dict):
    def __init__(self, names=(), values=(), **kwargs):
        super(Dict, self).__init__(**kwargs)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise

    def __setattr__(self, key, value):
        self[key] = value

@with_connection
def _select(sql, first, *args):
    global _db_ctx
    cusor = None
    sql = sql.replace('?', '%s')
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names, values)
        return [Dict(names, x) for x in cursor.fetchall()]
    finally:
        if cusor:
            cursor.close()

def select(sql, *args):
    return _select(sql, False, *args)

def select_one(sql, *args):
    return _select(sql, True, *args)

def select_id(sql, *args):
    d = _select(sql, True, *args)
    if d is None:
        return False
    return d.values()[0]

def insert(table, **kwargs):
    cols, args = zip(*kwargs.iteritems())
    sql = 'insert into `%s` (%s) values (%s)' % (table, ','.join(['`%s`' % col for col in cols]),
                                                 ','.join(['?' for i in range(len(cols))]))
    return _update(sql, *args)

@with_connection
def _update_many(sql, items):
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    try:
        cursor = _db_ctx.connection.cursor()
        for item in items:
            cursor.execute(sql, item)
        if _db_ctx.transactions == 0:
            _db_ctx.connection.commit()
        return 0
    except Exception as error:
        print(error)
    finally:
        if cursor:
            cursor.close()

@with_connection
def _update_one(sql, item):
    global _db_ctx
    cursor = None
    sql = sql.replace('?', '%s')
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql, item)
        r = cursor.rowcount
        if _db_ctx.transactions == 0:
            _db_ctx.connection.commit()
        return r
    except Exception as error:
        print(error)
    finally:
        if cursor:
            cursor.close()

def insert_many_update(table, items_all):
    items = []
    update_items = []
    for item in items_all:
        items.append(item['insert'])
        update_items.append(item['update'])
    item1 = items[0].items()
    cols, args = zip(*item1)
    update_item1 = update_items[0].items()
    update_cols, update_args = zip(*update_item1)
    update_item_list = []
    for item in update_items:
        col, arg = zip(*item.items())
        update_item_list.append(arg)
    item_list = []
    start = 0
    for item in items:
        col, arg = zip(*item.items())
        update_arg = update_item_list[start]
        all_arg = arg+update_arg
        item_list.append(all_arg)

    sql = 'insert into `%s` (%s) values (%s) ON DUPLICATE KEY UPDATE %s' % (table, ','.join(['`%s`' % col for col in cols]),
                                             ','.join(['?' for i in range(len(cols))]), ','.join([' `%s`=?' % col for col in update_cols]))
    return _update_many(sql, item_list)

def insert_one_update(table, item_all):
    item = item_all['insert']
    update_item = item_all['update']
    cols, args = zip(*item.items())
    update_cols, update_args = zip(*update_item.items())
    all_arg = args+update_args

    sql = 'insert into `%s` (%s) values (%s) ON DUPLICATE KEY UPDATE %s' % (table, ','.join(['`%s`' % col for col in cols]),
                                             ','.join(['?' for i in range(len(cols))]), ','.join([' `%s`=?' % col for col in update_cols]))
    return _update_one(sql, all_arg)