# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import json

from football.items import TeamItem, GameItem
import football.db.dbhelper as dbhelper

class FootballPipeline(object):
    def process_item(self, item, spider):
        if item.__class__ == TeamItem:
            try:
                rId = dbhelper.select_team_id(item['teamId'])
                if rId not in [19, 20, 21, 22, 23]:
                    update = {
                        'name': item['name'],
                    }
                else:
                    update = {
                        'rid': item['rid'],
                        'name': item['name'],
                    }
                #row = dbhelper.insert('team', rid=item['rid'], name=item['name'], teamId=item['teamId'])
                update_insert = {
                    'insert':{
                        'rid': item['rid'],
                        'name': item['name'],
                        'teamId': item['teamId'],
                    },
                    'update': update
                }
                row = dbhelper.update_insert_team('team', update_insert)
                print row
            except Exception as error:
                print error
        elif item.__class__ == GameItem:
            try:
                update = {
                    "insert":{
                        'homeTeam': item['homeTeam'],
                        'visitTeam': item['visitTeam'],
                        'round': item['round'],
                        'period': item['period'],
                        'rid': item['rid'],
                        'time': datetime.datetime.now(),
                        'homeScore': item['homeScore'],
                        'visitScore': item['visitScore'],
                        'matchId': item['matchId'],
                        'officialStartOdds': item['officialStartOdds'],
                        'bet365StartOdds': item['bet365StartOdds'],
                        'wlxeStartOdds': item['wlxeStartOdds'],
                        'bet365StartHandicap': item['bet365StartHandicap'],
                        'amcpStartHandicap': item['amcpStartHandicap'],

                        'lbStartOdds': item['lbStartOdds'],
                        'bwinStartOdds': item['bwinStartOdds'],
                        'bttStartOdds': item['bttStartOdds'],
                        'hgStartOdds': item['hgStartOdds'],
                        'officialEndOdds': item['officialEndOdds'],
                        'wlxeEndOdds': item['wlxeEndOdds'],
                        'lbEndOdds': item['lbEndOdds'],
                        'bet365EndOdds': item['bet365EndOdds'],
                        'bwinEndOdds': item['bwinEndOdds'],
                        'bttEndOdds': item['bttEndOdds'],
                        'hgEndOdds': item['hgEndOdds'],
                        'hgStartHandicap': item['hgStartHandicap'],
                        'bet365EndHandicap': item['bet365EndHandicap'],
                        'amcpEndHandicap': item['amcpEndHandicap'],
                        'hgEndHandicap': item['hgEndHandicap']
                    },
                    "update":{
                        'homeTeam': item['homeTeam'],
                        'visitTeam': item['visitTeam'],
                        'round': item['round'],
                        'period': item['period'],
                        'rid': item['rid'],
                        'time': datetime.datetime.now(),
                        'homeScore': item['homeScore'],
                        'visitScore': item['visitScore'],
                        'officialStartOdds': item['officialStartOdds'],
                        'bet365StartOdds': item['bet365StartOdds'],
                        'wlxeStartOdds': item['wlxeStartOdds'],
                        'bet365StartHandicap': item['bet365StartHandicap'],
                        'amcpStartHandicap': item['amcpStartHandicap'],

                        'lbStartOdds': item['lbStartOdds'],
                        'bwinStartOdds': item['bwinStartOdds'],
                        'bttStartOdds': item['bttStartOdds'],
                        'hgStartOdds': item['hgStartOdds'],
                        'officialEndOdds': item['officialEndOdds'],
                        'wlxeEndOdds': item['wlxeEndOdds'],
                        'lbEndOdds': item['lbEndOdds'],
                        'bet365EndOdds': item['bet365EndOdds'],
                        'bwinEndOdds': item['bwinEndOdds'],
                        'bttEndOdds': item['bttEndOdds'],
                        'hgEndOdds': item['hgEndOdds'],
                        'hgStartHandicap': item['hgStartHandicap'],
                        'bet365EndHandicap': item['bet365EndHandicap'],
                        'amcpEndHandicap': item['amcpEndHandicap'],
                        'hgEndHandicap': item['hgEndHandicap']
                    }
                }
                row = dbhelper.insert('game', update)
                print row
            except Exception as error:
                print item
        return item
