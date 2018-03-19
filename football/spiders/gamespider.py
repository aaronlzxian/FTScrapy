#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: aaron
# @File: gamespider.py
# @Time: 2018/2/23 15:28
# @Contact: liuzhongxian@jinuo.me
# @Description: demo
import re
import requests
import json

import scrapy

import football.db.dbhelper as dbhelper
from football.items import TeamItem, GameItem

class GameSpider(scrapy.Spider):
    name = 'game'
    allowed = ['www.okooo.com']
    root = 'http://www.okooo.com'
    oddsUrl = 'http://www.okooo.com/ajax/?method=data.match.odds'
    round_pa = re.compile(r'<a href="(/soccer/league/[\d]+/schedule/[\d]+/[\d\-]+/)" class="OddsLink"\s*>([\d]+)\s*</a>')
    period_pa = re.compile(ur'<li>·<a href="(/soccer/league/[\d]+/schedule/[\d]+/)" class="BlueWord_TxtL">[\u4e00-\u9fa5\s]*([\d\/]+)[\u4e00-\u9fa5\s]*</a></li>')
    game_pa = re.compile(ur'<tr matchid="([\d]*)" align="center" class="WhiteBg BlackWords">[\s]*<td.*>([\d\-\s\:]*)</td>[\s]*<td.*>(.*)</td>[\s]*<td.*>([\u4e00-\u9fa5\s]*)</td>[\s]*<td.*>[\s\S]*?<strong class="font_red">([\d\-]+)</strong>[\s\S]*?<td align="left">([\u4e00-\u9fa5\s]*)</td>[\s]*<td.*>([\d\.\-]*)</td>[\s]*<td.*>([\d\.\-]*)</td>[\s]*<td.*>([\d\.\-]*)</td>[\s\S]*?href="(.*?)"[\s\S]*?href="(.*?)"')
    game_pa2 = re.compile(ur'<tr matchid="([\d]*)" align="center" class="WhiteBg BlackWords">[\s]*<td.*>([\d\-\s\:]*)</td>[\s]*<td.*>(.*)</td>[\s]*<td.*>([\u4e00-\u9fa5\s]*)</td>[\s]*<td.*>([\d\-A-Z\s]*)</td>[\s]*<td.*>([\u4e00-\u9fa5\s]*)</td>[\s]*<td.*>([\d\.\-]*)</td>[\s]*<td.*>([\d\.\-]*)</td>[\s]*<td.*>([\d\.\-]*)</td>[\s\S]*?href="(.*?)"[\s\S]*?href="(.*?)"')
    markDict = {
        'officialStartOddsMark': '24_1',
        'wlxeStartOddsMark': '14_1',
        'bet365StartOddsMark': '27_1',
        'bet365StartHandicapMark': '27_2',
        'amcpStartHandicapMark': '84_2'
    }

    def __init__(self):
        race = dbhelper.select_race_all()
        team = dbhelper.select_team()
        if race is None or team is None:
            return False
        self.race = race
        self.teams = {}
        for item in team:
            name = item['name'].strip()
            self.teams[name] = item['id']

    def start_requests(self):
        for item in self.race:
            meta = {
                'race_id': item['id'],
            }
            url = 'http://www.okooo.com/soccer/league/{}/'.format(item['okoooId'])

            print("当前抓取的 Url 是：" + url)
            yield scrapy.Request(url, meta=meta)

    def parse(self, response):
        race_id = response.meta.get('race_id', 0)
        period_list = self.period_pa.findall(response.text)
        if period_list is not None:
            for period_url, period_time in period_list:
                period_url = '{}{}'.format(self.root, period_url)
                meta = {
                    'period_mark': period_time,
                    'race_mark': race_id
                }
                yield scrapy.Request(period_url, callback=self.parse_period, meta=meta)

    def parse_period(self, response):
        period_mark = response.meta.get('period_mark')
        race_mark = response.meta.get('race_mark')
        round_list = self.round_pa.findall(response.text)
        if round_list is not None:
            for round_url, round_number in round_list:
                item = GameItem()
                item['period'] = period_mark
                item['round'] = round_number
                item['rid'] = race_mark
                round_url = '{}{}'.format(self.root, round_url)
                yield scrapy.Request(round_url, callback=self.parse_round, meta={'item':item})

    def parse_round(self, response):
        item = response.meta.get('item')
        game_list = self.game_pa2.findall(response.text)
        if len(game_list) < 1:
            game_list = self.game_pa.findall(response.text)
        if game_list is not None:
            odds = {}
            matchIds = [matchId[0] for matchId in game_list]
            frist = True
            for game_item in game_list:
                matchId = game_item[0]
                if dbhelper.select_match_id(matchId):
                    return
                item['matchId'] = matchId
                item['round'] = game_item[2]
                homeTeamName = game_item[3].strip()
                item['homeTeam'] = self.teams[homeTeamName] if homeTeamName in self.teams else None
                score_str = game_item[4].strip()
                if score_str == 'VS':
                    homeScore = 0
                    visitScore = 0
                else:
                    score_list = score_str.split('-')
                    homeScore = score_list[0]
                    visitScore = score_list[1]
                item['homeScore'] = homeScore
                item['visitScore'] = visitScore
                visitTeamName = game_item[5].strip()
                item['visitTeam'] = self.teams[visitTeamName] if visitTeamName in self.teams else None
                if frist and len(matchIds) > 1:
                    odds = self.odds(matchIds)
                    frist = False
                officialStartOddsMark = '{}_{}'.format(matchId, self.markDict['officialStartOddsMark'])
                wlxeStartOddsMark = '{}_{}'.format(matchId, self.markDict['wlxeStartOddsMark'])
                bet365StartOddsMark = '{}_{}'.format(matchId, self.markDict['bet365StartOddsMark'])
                bet365StartHandicapMark = '{}_{}'.format(matchId, self.markDict['bet365StartHandicapMark'])
                amcpStartHandicapMark = '{}_{}'.format(matchId, self.markDict['amcpStartHandicapMark'])
                item['officialStartOdds'] = json.dumps(odds[officialStartOddsMark]) if officialStartOddsMark in odds else None
                item['wlxeStartOdds'] = json.dumps(odds[wlxeStartOddsMark]) if officialStartOddsMark in odds else None
                item['bet365StartOdds'] = json.dumps(odds[bet365StartOddsMark]) if officialStartOddsMark in odds else None
                item['bet365StartHandicap'] = json.dumps(odds[bet365StartHandicapMark]) if officialStartOddsMark in odds else None
                item['amcpStartHandicap'] = json.dumps(odds[amcpStartHandicapMark]) if officialStartOddsMark in odds else None
                yield item

    def odds(self, matchIds):
        result = {}
        try:
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Content-Length': '108',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'www.okooo.com',
                'Origin': 'http://www.okooo.com',
                'Referer': 'http://www.okooo.com/soccer/league/17/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
            }
            matchId_str = ','.join(matchIds).encode('utf-8')
            for key, val in self.markDict.iteritems():
                providerId, bettingTypeId= val.split('_')
                params = {
                    'matchIds': matchId_str,
                    'providerId': int(providerId),
                    'bettingTypeId': int(bettingTypeId),
                }
                response = requests.request("POST", self.oddsUrl, data=params, headers=headers)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    for key1, val1 in data.iteritems():
                        key1 = '{}_{}_{}'.format(key1, providerId, bettingTypeId)
                        result[key1] = val1
                else:
                    break
        except Exception as error:
            print error
        return result

class TeamSpider(scrapy.Spider):
    name = 'team'
    allowed = ['www.okooo.com']
    team_pa = re.compile(r'<td><a href="/soccer/team/([\d]+)/" target="_blank" class="BlueWord_TxtL">(.*)</a><br /></td>')
    team_pa2 = re.compile(ur'<td width="100">([\u4e00-\u9fa5\s]*)</td>')
    race_id_pa = re.compile(r'/league/([\d]+)')

    def __init__(self):
        race = dbhelper.select_race_all()
        if race is None:
            return False
        self.race = race

    def start_requests(self):
        for item in self.race:
            if item['id'] == 14:
                meta = {
                    'key':item['id']
                }
                #url = 'http://www.okooo.com/soccer/league/{}'.format(item['okoooId'])
                url = 'http://www.okooo.com/soccer/league/325/schedule/13153/'
                print("当前抓取的 Url 是：" + url)
                yield scrapy.Request(url, meta=meta)
            elif item['id'] == 17:
                meta = {
                    'key': item['id']
                }
                # url = 'http://www.okooo.com/soccer/league/{}'.format(item['okoooId'])
                url = 'http://www.okooo.com/soccer/league/40/schedule/13021/'
                print("当前抓取的 Url 是：" + url)
                yield scrapy.Request(url, meta=meta)
    def parse(self, response):
        race_id = response.meta.get('key', 0)
        if race_id == 1:
            print race_id
        if race_id > 0:
            team_name_list = self.team_pa.findall(response.text)
            if len(team_name_list) < 1:
                team_name_list = self.team_pa2.findall(response.text)
            if len(team_name_list) > 1:
                for team_id, team_name in team_name_list:
                    team = TeamItem()
                    team['rid'] = race_id
                    team['name'] = team_name
                    team['teamId'] = team_id
                    yield team
            else:
                print '未被抓取到的联赛ID：'+ str(race_id)
