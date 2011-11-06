#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
#   wps.py
#
#   PURPOSE:
#   Download schedule from womensprosoccer.com
#   Store applicable data in data structure.
#
#   TODO:
#

import sys
import re
import json
from BeautifulSoup import BeautifulSoup
from dget import GetSchedule

class WomensProSoccer(object):
    """Download schedule from official WPS website and process information."""
    
    def __init__(self):
        self.schedule = GetSchedule()
        self.url = "http://www.womensprosoccer.com/Home/schedule/2011-wps-schedule"
        #self.attribute = "modContent"
    
    def clean(self, html):
        """Remove all the html tags from a string."""
        
        count = 0
        html = unicode(html)
        soup = BeautifulSoup(html)
        for tag in soup.findAll(True):
            if tag.find('a'):
                if len(tag.contents[0]) > len(tag.contents[1]):
                    content = tag.contents[0]
                    content = [content]
                else:
                    content = tag.contents[1]
                    content = [content]
            elif len(soup.findAll(True)) == 2 and tag.contents == []:
                pass
            elif tag.contents == []:
                content = ['None']
            else:
                content = tag.contents
        
        return content[0]
        
    def crawl(self):
        """Crawl the page with BeautifulSoup for applicable information."""
        
        schedule = []
        
        soup = self.schedule.load_page(self.url)
        print 'Locating scheduling section'
        #section = soup.find("div", {"class": self.attribute})
        row_list = soup.find("tbody").findAll('tr')
        del row_list[0] # Remove table header
        del row_list[-6:] # Temporarily remove poorly formated final matches
        
        for row in row_list:
            info_list = row.findAll("div", {"align": "center"})
            
            if len(info_list) == 1:
                date = self.clean(info_list[0])
            else:
                match = {} # Dictionary to hold match information
                
                match['date'] = date
                match['team1'] = self.clean(info_list[0])
                match['team2'] = self.clean(info_list[1])
                match['venue'] = self.clean(info_list[2])
                match['score'] = self.clean(info_list[3])
                # Fourth element is a link to match report
                match['attendance'] = self.clean(info_list[5])
                print match
                
                # Add match dictionary to schedule list
                schedule.append(match)
                
        return schedule
        
    def score(self, section):
        """Process the score into number of (penalty) goals for each team"""
        
        match = {}
        
        section = section.contents
        if section[0] == 'Postponed':
            pass
        elif section[0] == '\n':
            #section = [item for item in section if item != '']
            print section
            section = BeautifulSoup(section).contents[1]
            print section
            match['goals1'] = int(section[0])
            match['goals2'] = int(section[8])
            match['pens1'] = int(section[3])
            match['pens22'] = int(section[11])
        else:
            section = section[0]
            match['goals1'] = int(section[0])
            match['goals2'] = int(section[4])
        
        return match
        
page = WomensProSoccer()
schedule = page.crawl()

with open('wps.json', 'w') as store:
    json.dump(schedule, store)
