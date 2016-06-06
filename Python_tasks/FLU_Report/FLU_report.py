from xml.sax import make_parser 
from xml.sax.handler import ContentHandler 
import csv
import sys
import os

fname = "flu_report.csv"

class EventHandler(ContentHandler):
    def __init__(self):
        self.flu_row = []
        self.flu_report = []
        self.week = ""
        self.year = ""
        self.state = False
        self.label = False

    def startElement(self, name, attr):
        if name == "timeperiod":
#       week number and year are attributes of parent tag "timeperiod"
#       will changed only after reading all child tags with states and prevalence
            self.week = attr.get("number")
            self.year = attr.get("year")
        if name == "abbrev":
            self.state = True
        if name == "label":
            self.label = True

    def endElement(self, name):
        self.state = False
        self.label = False

    def characters(self, content):
        if self.state:
            self.flu_row.append(self.week)
            self.flu_row.append(self.year)
            self.flu_row.append(content)
        if self.label:
            self.flu_row.append(content)
            self.flu_report.append(self.flu_row)
            self.flu_row = []



if __name__ == '__main__':

    url = "http://www.cdc.gov/flu/weekly/flureport.xml"

    parser = make_parser()
    handler = EventHandler()
    parser.setContentHandler(handler)

    parser.parse(url)

#   write to csv
    header = ["Week", "Year", "State", "Prevalence"]
    with open(fname, "wt") as f:
        writer = csv.writer(f, delimiter = ",")
        writer.writerow(header)
        writer.writerows(list(reversed(handler.flu_report)))
