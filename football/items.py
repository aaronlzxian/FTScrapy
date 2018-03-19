# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FootballItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class TeamItem(scrapy.Item):
    rid = scrapy.Field()
    name = scrapy.Field()
    teamId = scrapy.Field()

class GameItem(scrapy.Item):
    matchId = scrapy.Field()
    homeTeam = scrapy.Field()
    visitTeam = scrapy.Field()
    round = scrapy.Field()
    period = scrapy.Field()
    homeScore = scrapy.Field()
    visitScore = scrapy.Field()
    officialStartOdds = scrapy.Field()
    wlxeStartOdds = scrapy.Field()
    lbStartOdds = scrapy.Field()
    bet365StartOdds = scrapy.Field()
    bwinStartOdds = scrapy.Field()
    bttStartOdds = scrapy.Field()
    hgStartOdds = scrapy.Field()
    officialEndOdds = scrapy.Field()
    wlxeEndOdds = scrapy.Field()
    lbEndOdds = scrapy.Field()
    bet365EndOdds = scrapy.Field()
    bwinEndOdds = scrapy.Field()
    bttEndOdds = scrapy.Field()
    hgEndOdds = scrapy.Field()
    bet365StartHandicap = scrapy.Field()
    amcpStartHandicap = scrapy.Field()
    hgStartHandicap = scrapy.Field()
    bet365EndHandicap = scrapy.Field()
    amcpEndHandicap = scrapy.Field()
    hgEndHandicap = scrapy.Field()
    rid = scrapy.Field()