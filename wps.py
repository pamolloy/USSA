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

import re
import json
from BeautifulSoup import BeautifulSoup, NavigableString
from dget import GetSchedule

class WomensProSoccer(object):
    """Download schedule from official WPS website and process information."""
    
    def __init__(self):
        self.schedule = GetSchedule()
        self.url = "http://www.womensprosoccer.com/Home/schedule/2011-wps-schedule"
        
    def crawl(self):
        """Crawl the page with BeautifulSoup for applicable information."""
        
        schedule = []
        
        soup = self.schedule.load_page(self.url)
        print 'Locating scheduling section'
        tbody = soup.find("tbody").findAll('tr')
        del tbody[0] # Remove table header
        
        for row in tbody:
            stat = row.findAll("div", {"align": "center"})
            stat = [self.cleaner(info, 1) for info in stat] # Remove <div>
            
            # If the row consists of one column it contains the date. This is
            #quicker than searching for <th> with BeatifulSoup
            if len(stat) == 1:
                date = self.date(stat[0])
            else:
                match = {} # Dictionary to hold match information
                
                match['date'] = date # Assign the date of the last header row
                match['team1'] = stat[0][0]
                match['team2'] = stat[1][0]
                match['venue'] = stat[2][0]
                match.update(self.score(stat[3]))
                # Fourth element is a link to match report
                print stat[5]
                match['attendance'] = self.attendance(stat[5])
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
    
    def date(self, html):
        """Find the date in a table row. If playoff match create element."""
        
        row = self.cleaner(html, 1) # Remove <strong>
        
        if len(row) == 1:
            date = row[0]
        else: # Process ugly formatting of playoff games
            row = [element for element in row if isinstance(element, NavigableString)]
            date = row[-1] #TODO(pamolloy): Store game title
            
        return date
        
    def score(self, section):
        """Process the score into number of (penalty) goals for each team"""
        
        match = {}
        
        if section[0] == 'Postponed':
            pass
        elif section[0] == '\n': # Penalty goals
            section = section[1]
            goals = re.findall('\d', unicode(section))
            match['goals1'] = int(goals[0])
            match['goals2'] = int(goals[1])
            match['pens1'] = int(goals[2])
            match['pens2'] = int(goals[3])
        else:
            section = section[0]
            match['goals1'] = int(section[0])
            match['goals2'] = int(section[4])
        
        return match
       
    def attendance(self, html):
        """Find the attendance within list"""
        print html
        if len(html) == 1:
            attendance = html[0]
        elif len(html) == 2:
            print html
            attendance = [element for element in html if isinstance(element, NavigableString)]
            print attendance
            attendance = attendance[0]
        elif len(html) == 0: # Postponed game
            attendance = int() 
        
        return attendance

page = WomensProSoccer()
schedule = page.crawl()

print 'Storing schedule to: wps.json'
with open('wps.json', 'w') as store:
    json.dump(schedule, store)
