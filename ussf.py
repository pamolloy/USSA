#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
#   ussf.py
#
#   PURPOSE:
#   Download schedule from ussoccer.com
#   Store applicable data in data structure.
#
#   TODO:
#

import sys
import re
import json
from BeautifulSoup import BeautifulSoup, NavigableString
from ussa import GetSchedule

class USSoccer(object):
    """Download schedule from official USSF website and process information."""
    
    def __init__(self):
        self.schedule = GetSchedule()
        self.url = "http://www.ussoccer.com/Schedule-Tickets/Schedule.aspx"
        self.att = {"class": "genericTable"}
        
    def crawl(self):
        """Crawl the page with BeautifulSoup for applicable information."""
        
        schedule = []
        
        soup = self.schedule.load_page(self.url)
        print 'Locating scheduling section: {}'.format(self.att.values()[0])
        table = soup.find("table", self.att).findAll('tr')
        del table[0] # Remove table header
        
        for row in table:
            #stat = row.findAll("div", {"align": "center"})
            stats = row.contents
            stats = [element for element in stats if element != '\n']
            stats = [element.contents for element in stats] # Remove <td>
            
            match = {} # Dictionary to hold match information
            
            match['date'] = self.cleaner(stats[0], 1)[0]
            match['time'] = self.cleaner(stats[2], 1)[0]
            
            stadium = self.cleaner(stats[3][0], 1)[0]
            city = stats[3][2]
            match['venue'] = '{}, {}'.format(stadium, city)
            
            teams = stats[1][0]
            teams = teams.split(' vs. ')
            match['team1'] = teams[0]
            match['team2'] = teams[1]
            
            channels = stats[4][0]
            channels = channels.strip()
            if channels == '&nbsp;':
                pass
            else:
                channels = channels.split(', ')
                count = 0
                for station in channels:
                    match['tv{}'.format(count)] = station
                    count += 1
                
            # Fifth element is "Info Center"
            print match
            
            # Add match dictionary to schedule list
            schedule.append(match)
            
        return schedule
    
    def cleaner(self, html, repeat):
        """Recursively remove tags for a certain count, returning a list."""
        
        count = 0
        html = unicode(html)
        soup = BeautifulSoup(html)
        
        for element in soup.findAll(True):
            if count == repeat:
                break
            else:
                content = element.contents
                count += 1
                
        return content

page = USSoccer()
schedule = page.crawl()

print 'Storing schedule to: ussf.json'
with open('ussf.json', 'w') as store:
    json.dump(schedule, store)
