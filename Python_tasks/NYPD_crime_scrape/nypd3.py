import re
import os
import json
import csv
import requests
import ConfigParser
from lxml import html
from datetime import datetime

district_list = {
                         "PBBN": "Brooklyn North",
                         "PBBS": "Brooklyn South",
                         "PBBX": "Bronx",
                         "PBMN": "Manhattan North",
                         "PBMS": "Manhattan South",
                         "PBQN": "Queens North",
                         "PBQS": "Queens South",
                         "PBSI": "Staten Island"
                        }
crime_dict1 = {
                      "WTD_COMPLAINTS_Murder": "Murder",
                      "WTD_COMPLAINTS_Rape": "Rape",
                      "WTD_COMPLAINTS_Robbery": "Robbery",
                      "WTD_COMPLAINTS_Fel. Assault": "Felony Assault",
                      "WTD_COMPLAINTS_Burglary": "Burglary",
                      "WTD_COMPLAINTS_Gr. Larceny": "Grand Larceny",
                      "WTD_COMPLAINTS_G.L.A.": "Grand Larceny Auto"
               }
crime_dict2 = {
#                      "WTD_COMPLAINTS_Sht. Vic.": "Shooting Victims",
                      "WTD_COMPLAINTS_Sht. Inc.": "Shooting Incidents",
#                      "WTD_COMPLAINTS_Rape 1": "Rape 1",
                      "WTD_COMPLAINTS_Petit Larceny": "Petit Larceny",
                      "WTD_COMPLAINTS_Misd. Assault": "Misd. Assault",
                      "WTD_COMPLAINTS_Misd. Sex Crimes": "Misd. Sex Crime"
                     }
# read configuration from nypd_config.ini
config = ConfigParser.SafeConfigParser()
config.read("nypd_config.ini")

use_proxy = config.get("proxy", "use_proxy")
http_proxy = config.get("proxy", "http_proxy")
https_proxy = config.get("proxy", "https_proxy")

url = "https://compstat.nypdonline.org/api/reports/13/datasource/list"
url_week = "https://compstat.nypdonline.org/api/reports/1/datasource/list"

# some parameters for the requests
headers = {"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0",
           "Content-Type":"application/json;charset=utf-8",
           "Accept":"application/json, text/plain, */*",
           "Host": "compstat.nypdonline.org",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate, br",
           "Referer": "https://compstat.nypdonline.org/2e5c3f4b-85c1-4635-83c6-22b27fe7c75c/view/89",
           "Connection":"keep-alive",
          }
proxy_dict = {
              "http":http_proxy,
              "https":https_proxy
             }
payload = {"filters":[{"key":"PRECINCTKey","label":"Precinct","values":["Citywide"]},{"key":"BOROKey","label":"Patrol Borough","values":["Citywide"]},{"key":"RECORDID","label":"SELECTION","values":["WTD_COMPLAINTS_Rape"]}]}

# Parse title from response. Title contains subtype and date/time of crimes
def parse_title(metrics, doc):
    tree = html.fromstring(doc)
    crime_details = []
    for row in tree.xpath('//*[@class="text-left"]'):
        crime_details.append(" ".join(row.text_content().split()))

#   Almost all crimes under one type have the same format of titles.
#   Need to divide list on groups, n - number of elements in one group.
    n = int(len(crime_details)/metrics)

    if n >= 2:
#       Output list should include only two elements for each group - subtype and date+time.
#       Join all subtypes to one. For processing cases like Rape 1
        chunks=[crime_details[x:x+n] for x in range(0, len(crime_details), n)]
        crime_details = []
        for crime in chunks:
           while len(crime) > 2:
                t = []
                t.append(" ".join(crime[0:2]))
                for elem in crime[2:len(crime)]:
                    t.append(elem)
                crime = t
           crime_details.append(crime)
        return crime_details
    else:
#       if n <= 2 then no need to split list (for processing cases like Shooting Victims and Shooting incidents)
        t = []
        while len(t) < metrics:
            t.append(crime_details)
        crime_details = t
        return crime_details

# Define the week, for which we try to receive information
def get_week():
#       getting week
        if int(use_proxy) == 1:
            resp_week = requests.post(url_week, headers=headers, data = json.dumps(payload), proxies=proxy_dict)
        else:
            resp_week = requests.post(url_week, headers=headers, data = json.dumps(payload))
        if resp_week.status_code == 200:
            tree = html.fromstring(resp_week.json()[0]["RowLabel"])
            week = tree.xpath('//*[@class="pull-right"]/h4/text()')[0]
            return week
        else:
            print("Server returned code %s for %s" % (resp_week.status_code, url_week))
            return ""

# Getting information about crimes. Info is written in temporary file "temp.csv"
def scrape_crime():
        lists = []
        temp = []
        for district in district_list.keys():
            payload["filters"][0]["values"][0] = district
            print("Send request for district " + district_list[payload["filters"][0]["values"][0]])
            crime_dict = dict(crime_dict1, **crime_dict2)
            for crime in crime_dict.keys():
                payload["filters"][2]["values"][0] = crime
                if int(use_proxy) == 1:
                    response = requests.post(url, headers=headers, data = json.dumps(payload), proxies=proxy_dict, allow_redirects=True)
                else:
                    response = requests.post(url, headers=headers, data = json.dumps(payload))
                if response.status_code == 200:
                    for resp in response.json():
                        temp.append(district)
                        temp.append(crime)
                        temp.append(resp['Metric'])
                        temp.append(resp['Value'])
                        temp.append(resp['Title'])
                        lists.append(temp)
                        temp = []
                    print("Done for " + crime_dict[crime])
                else:
                    print("Server returned code %s for %s" % (response.status_code, url))
                    print(response.headers)
                    print(response.cookies)
                    print(response.request.headers)
                    return

        with open("temp.csv", "wb") as f:
            writer = csv.writer(f, delimiter = ",")
            for row in lists:
                if float(row[2]) > 0:
                    row[4] = parse_title(float(row[2]), row[4])
                else:
                    row[4] = []
                writer.writerow(row)
        return

# preparing list with data for writing to file
def data_preparing(week, ftemp):
                output = []
                shooting_incidents = []
                with open(ftemp, "rb") as ft:
                    reader = csv.reader(ft)
                    for row in reader:
#                       if subtype is not empty and metric (number of crimes) is not zero then parse row
                        if (row[4] != "[]") and (float(row[2]) > 0):
#                           find all elements between []
                            r = re.findall(r'\[(.*?)\]', row[4])
                            for cl in r:
                                line = []
                                line.append(district_list[row[0]])
                                try:
                                    line.append(crime_dict1[row[1]])
                                except KeyError:
                                    line.append(crime_dict2[row[1]])
                                long_lat = row[3].split(",")
                                line.append(long_lat[0])
                                line.append(long_lat[1])
                                cl = cl.replace(",", "").replace("[", "")
                                subtype = cl.split("' '")
                                line.append(subtype[0].replace("'", ""))
                                try:
                                    date_time = subtype[1].split(" ")
                                    line.append(date_time[0].replace("'", ""))
                                except Exception:
                                    line.append("Not defined")
                                try:
                                    time = datetime.strptime(date_time[1].replace("'", ""), "%I%p")
                                    line.append(time.strftime("%H:%M"))
                                except Exception:
                                    line.append("Not defined")
                                if (line[1] in crime_dict1.values()):
                                    line.append("Felony")
                                else:
                                    line.append("Misdemeanor")
                                line.append(week)
                                if line[1] != "Shooting Incidents":
                                     output.append(line)
                                else:
                                     shooting_incidents.append(line)
#                       rows with zero metric are skipped
#                        else:
#                            print("Skip row for: " + row[1] + row[3])
#               Processing shooting incidents. 
#               If record with the same district, coordinates and date/time are exist then skip this record,
#               else append to output list
                for s in shooting_incidents:
                    for out in output:
                        if (s[0]==out[0])and(s[2]==out[2])and(s[3]==out[3])and(s[5]==out[5])and(s[6]==out[6]):
                            break
                    else:
                        output.append(s)

                return output

# Write information to output file
def write_csv(week, data, fname):
    header = ["District", "Type", "Latitude", "Longitude", "Subtype", "Date", "Time", "Misdemeanor/Felony", "Week"]

#   if file doesn't exist then create it and write header
    if (not os.path.isfile(fname)):
            print("File doesn't exist, creating file...")
            with open(fname, "w") as f:
                writer = csv.writer(f, delimiter = ",")
                writer.writerow(header)

#   write prepared data to output file
    with open(fname) as inf, open("out_temp.csv", "w") as outf:
        reader = csv.reader(inf)
        writer = csv.writer(outf, delimiter = ",")
        for r in reader:
            if r[8] != week:
                writer.writerow(r)
        writer.writerows(data)
    os.remove(fname)
    os.rename("out_temp.csv", fname)
    return

if __name__ == '__main__':
    scrape_crime()
    week = get_week()

    output_file = config.get("file_settings", "output_file")
    if (week != "") and (os.path.isfile("temp.csv")):
        data = data_preparing(week, "temp.csv")
        write_csv(week, data, output_file)
        os.remove("temp.csv")
    else:
        print("No temporary file")

