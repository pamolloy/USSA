#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
#   dget.py
#
#   PURPOSE:
#   Download pages with United States soccer schedules and results. Store 
#   applicable data in data structure.
#
#   TODO:
#

import urllib2
import re
import json
from BeautifulSoup import BeautifulSoup

class GetSchedule(object): # TODO(pamolloy): Add object
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
        
