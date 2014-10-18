#!/usr/bin/python
# -*- coding: utf-8 -*-

import mechanize
from HTMLParser import HTMLParser
import re



url = 'https://www.visaservices.firm.in/Sweden-Russia-Tracking/Russia/Tracking.html'

br = mechanize.Browser()
br.open(url)
for link in br.links():
    siteMatch = re.compile('TrackingParam').search(link.url)
    if siteMatch:
        resp = br.follow_link( link )
        break


br.select_form(name="aspnetForm")

br["ctl00$CPH$txtR2Part1"] = ""
br["ctl00$CPH$txtR2Part2"] = ""
br["ctl00$CPH$txtR2Part3"] = ""
br["ctl00$CPH$txtR2Part4"] = ""
br["ctl00$CPH$txtDOB$txtDate"] = ""
response = br.submit()

content = response.get_data()
br.close()
match = re.search(r'<td>(.*)</td>', content)
if match:
    print match.group(1).replace('&#47;', '/')
else:
    print 'No results found'
