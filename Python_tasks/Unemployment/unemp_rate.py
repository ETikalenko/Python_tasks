import requests
import csv
import os
from lxml import html

url = "http://www.bls.gov/web/laus/lauhsthl.htm"

fname = "unemp_rate.csv"
ftemp = "temp.csv"

month_dict = {"Jan.": "01",
              "Feb.": "02",
              "Mar.": "03",
              "Apr.": "04",
              "May": "05",
              "June": "06",
              "July": "07",
              "Aug.": "08",
              "Sept.": "09",
              "Oct.": "10",
              "Nov.": "11",
              "Dec.": "12"}

class unempRateScrape():
    def __init__(self):
        self.month = ""
        pass

    def get_content(self):
        request = requests.get(url)
        tree = html.fromstring(request.content)
        nodes = tree.xpath("//table//tr")
        # rates and states
        data = [[td.text for td in node.xpath("td")] for node in nodes[3:]]
        # date, in word format
        header = tree.xpath("//table//th")[2]
        date = header.text.split()
        # take month number from dictionary
        self.month = month_dict[date[0]]
        temp = []
        output = []
        for row in data:
            temp.append(self.month)
            temp.append(date[1])
            temp.append(row[0])
            temp.append(row[1])            
            output.append(temp)
            temp = []

        return(output)

    def scrape(self, fname, ftemp):
        output = self.get_content()
        header = ["Month", "Year", "State", "Rate"]
        if not(os.path.isfile(fname)):
            with open(fname, "wt") as f:
                writer = csv.writer(f, delimiter = ",")
                writer.writerow(header)
                writer.writerows(output)
        else:
            # check for updates
            with open(fname, "r") as f:
                reader = csv.reader(f)
                # skip header
                header = next(reader)
                # check value of first cell in first row
                first_row = next(reader)
                if int(first_row[0]) == int(self.month):
                    print("No new month, update current month")
                    # need to update current month
                    with open(ftemp, "w") as outf:
                        writer = csv.writer(outf, delimiter = ",")
                        writer.writerow(header)
                        # write data for the current month
                        writer.writerows(output)
                        # exclude current month and write from input file to temp only previous months
                        for r in reader:
                            # write data only if it is previous months
                            if not(int(r[0]) == int(self.month)):
                                writer.writerow(r)
                        os.remove(fname)
                        os.rename(ftemp, fname)
                else:
                    print("Updating...")
                    # update file
                    with open(ftemp, "w") as outf:
                        writer = csv.writer(outf, delimiter = ",")
                        writer.writerow(header)
                        # write current information
                        writer.writerows(output)
                        # write previous information
                        writer.writerow(first_row)
                        for r in reader:
                            writer.writerow(r)
                    os.remove(fname)
                    os.rename(ftemp, fname)

if __name__ == "__main__":
   scraper = unempRateScrape()
   scraper.scrape(fname, ftemp)

