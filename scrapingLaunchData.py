#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import requests
from datetime import datetime,timezone
import pandas as pd

#########################
# library needed
# - bs4
# - pandas
# - requests
#########################

# get orbital launches html text
url = "https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches"
page = requests.get(url).text
page_content = BeautifulSoup(page, 'html.parser')


# a list of string marks a launch as success
success_marks = ['Successful', 'Operational', 'En Route']

# remove string after a start bracket to remove notes tail
def removeAfterBracket(string):
    p = string.find("[")
    if(p != -1):
        return string[:p]
    return string

def getSuccessDateWithNum(page_content):
    # dict to store date and num
    success_date = {}
    
    # get launches table
    table = page_content.find("table",class_="wikitable collapsible")
    
    # indict if found a launch date
    found_date = False
    
    for row in table.findAll('tr'):
        row_data = row.findAll("td")
        for td in row_data:
            if_date = td.find("span",class_="nowrap")
            # check if date occurred
            # if it is date of launch by check if it spans rows
            if(if_date is not None and td['rowspan'] != "1"):
                found_date = True
                date_ = removeAfterBracket(if_date.get_text())
                break
        # when date found, check if there is at least one successful launch
        if(found_date and removeAfterBracket(row_data[-1].get_text().strip()) in success_marks):
            found_date = False
            if(date_ in success_date):
                success_date[date_]+=1
            else:
                success_date[date_]=1
    return success_date

def date2isoformat(success_date):
    date_iso_dict = {}
    for d,n in success_date.items():
        day = int(d.split()[0].strip())
        month = d.split()[1].strip()
        
        # convert string to iso format
        full_date = datetime.strptime(month, '%B').replace(year=2019,day=day,tzinfo=timezone.utc)
        date_in_iso = full_date.isoformat()
        
        date_iso_dict[date_in_iso] = n
    return date_iso_dict


success_date = getSuccessDateWithNum(page_content)
date_iso_dict = date2isoformat(success_date)

# generate all days in 2019
pd_days = pd.date_range(start ='1-1-2019',  
         end ='12-31-2019', freq ='D',tz="UTC") 

days = []
launch_num = []
for d in pd_days:
    d = d.isoformat()
    days.append(d)
    #append 0 or value if existing sucessful launch
    if(d in date_iso_dict):
        launch_num.append(date_iso_dict[d])
    else:
        launch_num.append(0)
        
data ={"date":days, "value":launch_num}
df = pd.DataFrame(data)
df.to_csv("Example_output.csv")

