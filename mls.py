#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
#   mls.py
#
#   PURPOSE:
#   Download schedule from mlssoccer.com
#   Store applicable data in data structure.
#
#   TODO:
#

import re
import json
from BeautifulSoup import BeautifulSoup, NavigableString
from ussa import GetSchedule

class MLSSoccer(object):
    """Download schedule from official MLS website and process information."""
    
    def __init__(self):
        self.schedule = GetSchedule()
        self.url = "http://www.mlssoccer.com/schedule?month=all&year=2011"
        self.att = "schedule-page"
    
    def crawl(self):
        """Crawl the page with BeautifulSoup for applicable information."""
        
        schedule = []
        
        soup = self.schedule.load_page(self.url)
        print 'Locating scheduling section: {}'.format(att)
        section = soup.find("div", {"class": self.att})
        
        for table in section.findAll("table"):
            table_body = table.find('tbody')
            date = self.date(table)
            table_rows = table_body.findAll('tr')
            
            for row in table_rows:
                
                match = {}
                
                # NOT easily processed information
                match['date'] = date
                details = self.details(row)
                match.update(details)
                goals = self.score(row)
                match.update(goals)
                
                # Easily processed information
                match['venue'] = self.generic(row, "views-field venue")
                match['team1'] = self.generic(row, "views-field home-team")
                match['team2'] = self.generic(row, "views-field away-team")
                
                # Add match dictionary to schedule list
                schedule.append(match)
                
        return schedule
        
    def date(self, section):
        """Find the date of each match based on the last preceding <h3> tag"""
        
        date = section.findPreviousSibling("h3")
        date = BeautifulSoup(unicode(date))
        date = date.h3.contents[0] # Remove tags
        
        return date
        
    def details(self, section):
        """Process the venue and channels from the details section"""
        
        match = {}
        
        html = section.find("td", {"class": "views-field start-time"})
        details = html.contents
        
        # If the game has passed, ignore "Final"
        if details[0] == u'Final':
            return match
        else:
            match['hour'] = details[0]
            count = 0
            channels = html.findAll('strong')
            for station in channels:
                station = BeautifulSoup('{}'.format(station))
                match['tv{}'.format(count)] = station.strong.contents[0]
                count += 1
            
            return match
            
    def score(self, section):
        """Process the score into number of (penalty) goals for each team"""
        
        match = {}
        score = section.find("td", {"class": "views-field score"}).contents
        # Ignore score for upcoming games, which return empty list
        if score == []:
           return match 
        else:
            score = score[0] # Select first string from list
            # Store penalties
            if re.search('(\(|\))', score):
                match['goals1'] = int(score[0])
                match['goals2'] = int(score[8])
                match['pens1'] = int(score[3])
                match['pens2'] = int(score[11])
            elif re.search('[0-9]', score):
                match['goals1'] = int(score[0])
                match['goals2'] = int(score[4])
            else: pass
            
            return match
            
    def generic(self, section, attribute):
        """Find and return the match venue."""
        
        info = section.find("td", {"class": attribute}).contents[0]
        
        return info
        
page = MLSSoccer()
schedule = page.crawl()

print 'Storing schedule to: mls.json'
with open('mls.json', 'w') as store:
    json.dump(schedule, store)

