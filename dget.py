#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#   dget.py
#
#   PURPOSE:
#   Download pages with United States soccer schedules and results. Store 
#   applicable data in data structure.
#
#   TODO:
#   - Split into multiple files by class
#   - Apply processing in MLSSoccer recursively inside tables
#   - Check national team player pool and check upcoming games for applicable
#     players

import urllib2
import re
import json
from BeautifulSoup import BeautifulSoup

class GetSchedule:
    """Download pages with United States soccer schedules and results. Store
     applicable data in external JSON data structure."""
    
    def __init__(self):
        pass # Select which websites to crawl
        
    def load_page(self, url):
        """For each URL in the given list: download the page, read it"""
        
        print 'Downloading: {}'.format(url)
        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page)
        
        return soup
        
class MLSSoccer:
    """Download schedule from official MLS website and process information."""
    
    def crawl(self):
        mls_list = []
        url = "http://www.mlssoccer.com/schedule?month=all&year=2011"
        schedule = GetSchedule()
        soup = schedule.load_page(url)
        print 'Locating scheduling section'
        section = soup.find("div", {"class": "schedule-page"})
        
        for table in section.findAll("table"):
            match = {}
            
            # NOT easily processed information
            match['date'] = self.date(table)
            details = self.details(table) # TODO(pamolloy): Clarify output
            match = dict(match.items() + details.items())
            goals = self.score(table) # TODO(pamolloy): Clarify output
            match = dict(match.items() + goals.items())
            
            # Easily processed information
            match['venue'] = self.generic(table, "views-field venue")
            match['team1'] = self.generic(table, "views-field home-team")
            match['team2'] = self.generic(table, "views-field away-team")
            
            # Add match dictionary to schedule list
            mls_list.append(match)
            
        return mls_list
        
    def date(self, table):
        """Find the date of each match based on the last <h3> tag"""
        
        date = table.findPreviousSibling("h3") # Find last preceding <h3> tags
        date = BeautifulSoup('{}'.format(date))
        date = date.h3.contents[0] # Remove <h3> tags
        
        return date
        
    def details(self, table):
        """Process the venue and channels from the details section"""
        
        match = {}
        html = table.find("td", {"class": "views-field start-time"})
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
            
    def score(self, table):
        """Process the score into number of (penalty) goals for each team"""
        
        match = {}
        score = table.find("td", {"class": "views-field score"}).contents
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
        
    def generic(self, table, attribute):
        """Find and return the match venue."""
        
        info = table.find("td", {"class": attribute}).contents[0]
        
        return info
        
        
x = MLSSoccer()
y = x.crawl()

with open('mls.json', 'w') as store:
    json.dump(y, store)

