import requests
import datetime
import csv
import os
from lxml import html

url = "http://www.sca.isr.umich.edu/files/tbmics.csv"
fname = "ics_report.csv"

class SentimentScrape():
    def __init__(self):
        pass

    def get_content(self, url):
        req = requests.get(url)
        data = req.content.split("\n")

        if data[len(data)-1] == "":
            del(data[len(data)-1])
        current_data = data[len(data)-1].split(",")

        ics = current_data[2].replace("\r", "")
        ics_prev = data[len(data)-2].split(",")[2].replace("\r", "")
        
        change = (float(ics) - float(ics_prev))*100/float(ics_prev)

        output = [datetime.datetime.strptime(current_data[0], "%B").strftime("%m"), current_data[1], ics, round(change, 2)]
        return(output)

    def write_csv(self, fname, data):
        ftemp = "temp.csv"
        header = ["Month", "Year", "ICS", "Change (prev.month,%)"]
        if not(os.path.isfile(fname)):
            print("Create new file...")
            with open(fname, "wb") as inpf:
                writer = csv.writer(inpf)
                writer.writerow(header)
                writer.writerow(data)
        else:
            print("Updating file...")
            #   check if there is a new information
            #   read first row to check week
            with open(fname, "rb") as inpf:
                reader = csv.reader(inpf)
                # skip header
                header = next(reader)
                first_row = next(reader)
                with open(ftemp, "wb") as outf:
                    writer = csv.writer(outf)
                    writer.writerow(header)
                    writer.writerow(data)
                    # if month is differ from month in csv then add new row
                    # else update current row
                    if first_row[0] != data[0]:
                        writer.writerow(first_row)
                    for r in reader:
                        writer.writerow(r)

            os.remove(fname)
            os.rename(ftemp, fname)


if __name__ == "__main__":
    scraper = SentimentScrape()
    data = scraper.get_content(url)
    scraper.write_csv(fname, data)
