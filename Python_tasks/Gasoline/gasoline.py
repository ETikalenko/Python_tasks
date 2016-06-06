import requests
import csv
import sys
import os
from lxml import html

base_url = "http://www.eia.gov/dnav/pet/"
fname = "gasoline_price.csv"
gas_dict = {"pet_pri_gnd_a_epm0u_pte_dpgal_w.htm": "All Grades - Conventional Areas",
        "pet_pri_gnd_a_epm0r_pte_dpgal_w.htm": "All Grades - Reformulated Areas",
        "pet_pri_gnd_a_epmr_pte_dpgal_w.htm": "Regular",
        "pet_pri_gnd_a_epmru_pte_dpgal_w.htm": "Regular - Conventional Areas",
        "pet_pri_gnd_a_epmrr_pte_dpgal_w.htm": "Regular - Reformulated Areas",
        "pet_pri_gnd_a_epmmu_pte_dpgal_w.htm": "Midgrade - Conventional Areas",
        "pet_pri_gnd_a_epmmr_pte_dpgal_w.htm": "Midgrade - Reformulated Areas",
        "pet_pri_gnd_a_epmm_pte_dpgal_w.htm": "Midgrade",
        "pet_pri_gnd_a_epmp_pte_dpgal_w.htm": "Premium",
        "pet_pri_gnd_a_epmpu_pte_dpgal_w.htm": "Premium - Conventional Areas",
        "pet_pri_gnd_a_epmpr_pte_dpgal_w.htm": "Premium - Reformulated Areas",
        "pet_pri_gnd_a_epd2d_pte_dpgal_w.htm": "Diesel - All Types",
        "pet_pri_gnd_a_EPD2DXL0_pte_dpgal_w.htm": "Ultra Low Sulfur Diesel",
#        exclude as information for Low Sulfur Diesel doesn't update from 2008
#        "pet_pri_gnd_a_EPD2DM10_pte_dpgal_w.htm": "Low Sulfur Diesel"
        }

class GasolinePrices():
    def __init__(self):
        pass

    def get_content(self, base_url):
        output = []
        for gas in gas_dict.keys():
            url = base_url + gas
            req = requests.get(url)
            tree = html.fromstring(req.content)
            # all information in table between tags <tr>
            nodes = tree.xpath("//table//tr")

            # current date is the last but one in header. Get header and then take only last date.
            temp = []
            for node in nodes[0:]:
                for th in node.xpath("th"):
                    t = th.text
                    temp.append(t)
            date = temp[len(temp)-2]

            temp = []
            data = []
            # start from 16 node for excluding information from header. Get only rows from table
            for node in nodes[16:]:
                for td in node:
                    t = td.text
                    if t is not None:
                        t = t.replace("\n", "").replace("\t", "").replace("\r", "").encode("utf-8")
                    temp.append(t)
                data.append(temp)
                temp = []

            # data is list of lists, need to merge every two lists as first is prices, second is an area
            # break list on chunks by two
            chunks = [data[x:x+2] for x in range(0, len(data), 2)]
            data = []
            # at first area type is US
            area_type = "US"
            for d in chunks:
                try:
                    # for excluding unwanted info, take only that chunks which have length 2
                    if len(d) == 2:
                        # if the row with States or Cities appeared then change type of area
                        if d[1][1] == "States":
                            area_type = "State"
                        if d[1][1] == "Cities":
                            area_type = "City"
                        # exclude from output rows with headers States and Cities
                        if d[1][1] != "States" and d[1][1] != "Cities":
                            # date, area type, area, product, price
                            temp = [date, area_type, d[1][1], gas_dict[gas], d[0][6]]
                            data.append(temp)
                        temp = []
                # IndexError when the info about prices is finished
                except IndexError:
                    break

            # for the first row add U.S.. It wasn't retrieved because of US stored between tags <td><B>U.S.<B></td>
            # all another areas stored between td: <td>East Coast (PADD1)</td>
            data[0][2] = "U.S."
            output.extend(data)
        return(output)

    def write_csv(self, fname, data):
        header = ["Date", "Area Type", "Area", "Product", "Price"]
        ftemp = "temp.csv"

        if (not os.path.isfile(fname)):
            print("File doesn't exist, creating file...")
            with open(fname, "wb") as inpf:
                writer = csv.writer(inpf, delimiter = ",")
                writer.writerow(header)
                writer.writerows(data)
        else:
            print("Updating file...")
            #   check if there is a new information
            #   read first row to check the date
            with open(fname, "rb") as inpf:
                reader = csv.reader(inpf)
                # skip header
                header = next(reader)
                first_row = next(reader)
                with open(ftemp, "wb") as outf:
                    writer = csv.writer(outf)
                    writer.writerow(header)
                    writer.writerows(data)
                    # if data is new information then write first row and all remaining info from file
                    if first_row[0] != data[0][0]:
                        writer.writerow(first_row)
                    # for the case if for different products info will be updated for different dates
                    # check date for every row from output file with every row from data
                    i = 0
                    for r in reader:
                        i = i + 1
                        if i < len(data):
                            if r[0] != data[i][0]:
                                writer.writerow(r)
                        else:
                            writer.writerow(r)
            os.remove(fname)
            os.rename(ftemp, fname)
                            


if __name__ == "__main__":
    scraper = GasolinePrices()
    data = scraper.get_content(base_url)
    scraper.write_csv(fname, data)

