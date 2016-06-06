import csv
import urllib
import requests
import sys
import os
from xml.sax import make_parser 
from xml.sax.handler import ContentHandler
from datetime import datetime


api_key = "YOUR_API_KEY"
base_url = "http://api.eventful.com/rest/events/search?app_key="
vfile = "Venues_id.csv"
fname = "future_events.csv"

# function to get information for each venue
# Input: id of venue
# Output: list of events in given venue in output format
class EventHandler(ContentHandler):

    def __init__(self):
        self.tag_list = [""]
        self.page_count = False
        
#       for events list
        self.id = ""
        self.title = False
        self.start_date = False
        self.stop_date = False
        self.venue_name = False
        self.venue_address = False
        self.venue_city = False
        self.venue_state = False
        self.venue_zip = False
        self.venue_lat = False
        self.venue_lng = False

#       final lists with events and venues
        self.event_list = []
        self.max_page = ""

        self.event = ["", "", "", "", "", "", "", "", "", "", "", ""]
        self.content = ""
        self.address = ""
        self.start = ""
        self.stop = ""
        self.vname = ""
        self.lat = ""
        self.lng = ""

    def startElement(self, name, attr):
        if name == "page_count":
            self.page_count = True
        if name == "event":
            self.id = attr.get("id")
        if name == "title":
            self.title = True
        if name == "start_time":
            self.start_date = True
        if name == "stop_time":
            self.stop_date = True
        if name == "venue_name":
            self.venue_name = True
        if name == "venue_address":
            self.venue_address = True
        if name == "city_name":
            self.venue_city = True
        if name == "region_abbr":
            self.venue_state = True
        if name == "postal_code":
            self.venue_zip = True
        if name == "latitude":
            self.venue_lat = True
        if name == "longitude":
            self.venue_lng = True

    def endElement(self, name):
        self.page_count = False
        if self.title and name == "title":
            self.title = False
#           title will be encoded to utf-8
            self.event[4] = unicode(self.content).encode('utf8')
            self.content = ""
        if self.start_date:
            self.start_date = False
            self.event[1] = unicode(self.start).encode('utf8')
            self.start = ""
        if self.stop_date:
            self.stop_date = False
            self.event[2] = unicode(self.stop).encode('utf8')
            self.stop = ""
        if self.venue_name:
            self.venue_name = False
            self.event[3] = unicode(self.vname).encode('utf8')
            self.vname = ""
        if self.venue_address:
            self.venue_address = False
            self.event[5] = unicode(self.address).encode('utf8')
            self.address = ""
        self.venue_city = False
        self.venue_state = False
        self.venue_zip = False
        if self.venue_lat:
            self.venue_lat = False
            self.event[9] = self.lat.encode('ascii', 'replace')
            self.lat = ""
        if self.venue_lng:
            self.venue_lng = False
            self.event[10] = self.lng.encode('ascii', 'replace')
            self.lng = ""
            self.event_list.append(self.event)
            self.event = ["", "", "", "", "", "", "", "", "", "", "", ""]

    def characters(self, content):
        if self.page_count:
           self.max_page = content
        if self.title:
            self.event[0] = self.id
            self.content += content
            
        if self.start_date:
            self.start += content
        if self.stop_date:
            self.stop += content
        if self.venue_name:
            self.vname += content
        if self.venue_address:
            self.address += content
        if self.venue_city:
            self.event[6] = content
        if self.venue_state:
            self.event[7] = content
        if self.venue_zip:
            self.event[8] = content
        # sometimes in lat & lng also there are some weird symbols... (E0-001-093146159-9)
        if self.venue_lat:
            self.lat += content
#            self.event[9] = content
        if self.venue_lng:
            self.lng += content
#            self.event[10] = content

def write_csv(event_list, fname):
    ftemp = "temp.csv"
    header = ["Event id", "Event start date", "Event stop date", "Venue name", "Event name", "Venue address", "Venue city", "Venue state", "Postal code", "Latitude", "Longitude", "Cancelled"]
    # if output file doesn't exist then create it
    if not(os.path.isfile(fname)):
        print("Create file...")
        with open(fname, "wb") as inpf:
            writer = csv.writer(inpf, delimiter = ";")
            writer.writerow(header)
            writer.writerows(event_list)
    else:
        # need:
        # 1. write new events
        # 2. update old events
        # 3. check on cancelled events (such event is deleted from list of events for venue)

        with open(fname, "rb") as inpf:
            print("Updating file...")
            reader = csv.reader(inpf, delimiter = ";")
            # skip header
            header = next(reader)
            # get current date
            cur_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            future_events = []
            output = []
            with open(ftemp, "wb") as outf:
                writer = csv.writer(outf, delimiter = ";")
                writer.writerow(header)
                # collect current events from file
                # for each event from file: event is current if it has stop_time greater than current date or
                # if it has empty stop_time and start_time greater than current time.
                for r in reader:
                    if r[2] != "":
                        if datetime.strptime(r[2], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") >= cur_date:
                            future_events.append(r)
                        else:
                            output.append(r)
#                            writer.writerow(r)
                    else:
                        if datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") >= cur_date:
                            future_events.append(r)
                        else:
                            output.append(r)
#                            writer.writerow(r)
                # check if we have cancelled events: search event in input list. If not found then event was cancelled - 
                # marked it as Cancelled and write it to output
                for e in future_events:
                    find = 1
                    for el in event_list:
                        if e[0] == el[0]:
                            find = 0
                            break
                    if find == 1:
                        e[11] = "Cancelled"
                        output.append(e)
#                        writer.writerow(e)
                    
                # after checking write all search results to output (input list contains new events and updated info for current events)
                # additionally need to check if past events is still in search results (e.g., possible situation for today's events)
                for el in event_list:
                    add = 1
                    for out in output:
                        if el[0] == out[0]:
                            add = 0
                            break
                    if add == 1:
                        output.append(el)
#                        writer.writerow(el)
                # write to file, list is sorted by date, recent data is at the top
                writer.writerows(sorted(output, key=lambda date: datetime.strptime(date[1], "%Y-%m-%d %H:%M:%S"), reverse=True))
            os.remove(fname)
            os.rename(ftemp, fname)


if __name__ == "__main__":
    # get list of venues ids from csv file
    venue_list = []
    with open(vfile, "rb") as f:
        reader = csv.reader(f)
        for r in reader:
            venue_list.append(r[5])

#   get xml for each venue and parse it
    output_list = []
    for vid in venue_list:
        print("Loading data for venue id = " + vid)
        url1 = base_url + api_key + "&location=" + vid + "&page_size=100&sort_order=date"
        # get number of pages
        parser = make_parser()
        handler = EventHandler()
        parser.setContentHandler(handler)
        parser.parse(urllib.urlopen(url1))
        max_page = handler.max_page
        del handler

        if int(max_page) > 0:
            page_num = 1
            while page_num <= int(max_page):
                url = url1 + "&page_number=" + str(page_num)
                handler = EventHandler()
                parser.setContentHandler(handler)
                parser.parse(urllib.urlopen(url))
                event_list = handler.event_list
                output_list.extend(event_list)
                del handler
                page_num += 1

    write_csv(output_list, fname)
