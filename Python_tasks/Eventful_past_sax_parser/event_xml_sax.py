from xml.sax import make_parser 
from xml.sax.handler import ContentHandler 
import csv
import sys

class EventHandler(ContentHandler):

    def __init__(self):
        self.tag_list = [""]
#       for events list
        self.title = False
        self.start_date = False
        self.venue_id = False
        self.popularity = False
#       for venue list
        self.vid = False
        self.venue_name = False
        self.vpopularity = False
        self.venue_address = False
        self.venue_city = False
        self.venue_state = False
        self.venue_zip = False
        self.venue_lng = False
        self.venue_lat = False
#       final lists with events and venues
        self.events_list = []
        self.venues_list = []
#       list for each event and venue
        self.event = ["NA", "NA", "NA", "NA"]
        self.venue = ["NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
#       to check if section performers started
        self.performers = False
#       fields for collecting content
        self.content = ""
        self.id_event = ""
        self.date = ""
        self.id = ""
        self.lat = ""
        self.lng = ""
        self.vname = ""
        self.addr = ""
        self.city = ""
        self.state = ""
        self.zip = ""


    def startElement(self, name, attr):
#       if section has tag short_bio then it's performers section, need to skip
        if (name == "short_bio"):
            self.performers = True
        else:
#           to keep track of where in the tree will need to check previous tag 
#           needed as different section has tags with the same names (but the order of tags are different).
#           extract info for event lists
            if ((self.tag_list[-1] == "url") and (name == "title")):
                self.title = True
            if ((self.tag_list[-1] == "description") and (name == "start_time")):
                self.start_date = True
            if ((self.tag_list[-1] == "stop_time") and (name == "venue_id")):
                self.venue_id = True
            if ((self.tag_list[-1] == "modified") and (name == "popularity")):
                self.popularity = True
#           extract info for venue list. Check that previous tag is "venue" as this part begins as performers
            if ((self.tag_list[-1] == "venue") and (name == "id")):
                self.vid = True
            if ((self.tag_list[-1] == "url") and (name == "name")):
                self.venue_name = True
            if ((self.tag_list[-1] == "venue_display") and (name == "address")):
                self.venue_address = True
            if ((self.tag_list[-1] == "address") and (name == "city")):
                self.venue_city = True
            if ((self.tag_list[-1] == "region") and (name == "region_abbr")):
                self.venue_state = True
            if ((self.tag_list[-1] == "region_abbr") and (name == "postal_code")):
                self.venue_zip = True
            if ((self.tag_list[-1] == "country_abbr") and (name == "latitude")):
                self.venue_lat = True
            if ((self.tag_list[-1] == "latitude") and (name == "longitude")):
                self.venue_lng = True
            if ((self.tag_list[-1] == "withdrawn_note") and (name == "popularity")):
                self.vpopularity = True
#           filling tag list
            self.tag_list.append(name)


    def endElement(self, name):
        if self.title and name == "title":
            self.title = False
#           title will be encoded to utf-8. For other field ascii simbols will be ignored
            self.event[1] = unicode(self.content).encode('utf8')
            self.content = ""
        if self.start_date and name == "start_time":
            self.start_date = False
            self.event[0] = (self.date).encode('ascii', 'replace')
            self.date = ""
        if self.venue_id and name == "venue_id":
            self.venue_id = False
            self.event[2] = (self.id_event).encode('ascii', 'ignore')
            self.id_event = ""
        self.popularity = False
        if self.vid and name == "id":
            self.vid = False
            self.venue[0] = unicode(self.id).encode('utf8')
            self.id = ""
        if self.venue_name and name == "name":
            self.venue_name = False
            self.venue[1] = (self.vname).encode('ascii', 'ignore')
            self.vname = ""
        self.vpopularity = False
        if self.venue_address and name == "address":
            self.venue_address = False
            self.venue[2] = (self.addr).encode('ascii', 'ignore')
            self.addr = ""
        if self.venue_city and name == "city":
            self.venue_city = False
            self.venue[3] = (self.city).encode('ascii', 'ignore')
            self.city = ""
        if self.venue_state and name == "region_abbr":
            self.venue_state = False
            self.venue[4] = (self.state).encode('ascii', 'ignore')
            self.state = ""
        if self.venue_zip and name == "postal_code":
            self.venue_zip = False
            self.venue[5] = (self.zip).encode('ascii', 'ignore')
            self.zip = ""
        if self.venue_lng and name == "longitude":
            self.venue_lng = False
            self.venue[7] = (self.lng).encode('ascii', 'ignore')
            self.lng = ""
        if self.venue_lat and name == "latitude":
            self.venue_lat = False
            self.venue[6] = (self.lat).encode('ascii', 'ignore')
            self.lat = ""

    def characters(self, content):
        if self.performers is False:
#           fill events list
#           appending in endElements. Need to collect content in such way to process special 
#           characters in fields (e.g. in some cases title or id is on different lines)
            if self.title:
                self.content += content 
            if self.start_date:
                self.date += content
            if self.venue_id:
                self.id_event += content
            if self.popularity:
#           for popularity append here (as two different tags with the same name)
                self.event[3] = (content).encode('ascii', 'replace')                
                self.events_list.append(self.event)
                self.event = ["NA", "NA", "NA", "NA"]
#           fill venue list
            if self.vid:
                self.id += content
            if self.venue_name:
                self.vname += content
            if self.venue_address:
                self.addr += content
            if self.venue_city:
                self.city += content
            if self.venue_state:
                self.state += content
            if self.venue_zip:
                self.zip += content
            if self.venue_lat:
                self.lat += content
            if self.venue_lng:
                self.lng += content
            if self.vpopularity:
                self.venue[8] = (content).encode('ascii', 'replace')
                self.venues_list.append(self.venue)
                self.venue = ["NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]



if __name__ == '__main__':

    if len(sys.argv) == 1:
        print "Please enter the file name...."
        sys.exit()
        
    fname = sys.argv

    parser = make_parser()
    handler = EventHandler()
    parser.setContentHandler(handler)

    print("Reading file..." + str(fname[1]))

    parser.parse(str(fname[1]))

    event_list = handler.events_list
    venue_list = handler.venues_list
    print(len(handler.events_list))
    print(len(handler.venues_list))

    del handler

    output = []
    i = 0
#   search for each event the venue where this event took place
    for event in event_list:
        i = i + 1
        if i % 1000 == 0: print("Processed... " + str(i))
        temp = []
        for venue in venue_list:
            if venue[0] == event[2]:
                temp.append(event[0])
                temp.append(venue[1])
                temp.append(venue[8])
                temp.append(event[1])
                temp.append(event[3])
                temp.append(venue[2])
                temp.append(venue[3])
                temp.append(venue[4])
                temp.append(venue[5])
                temp.append(venue[6])
                temp.append(venue[7])
                break
        if temp:
            output.append(temp)
#   write csv
    header = ["Date", "Venue name", "Venue popularity", "Event name", "Event popularity", "Venue address", "City", "State", "Zip code", "Latitude", "Longitude"]
    with open("test.csv", "wt") as f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerow(header)
        writer.writerows(output)


