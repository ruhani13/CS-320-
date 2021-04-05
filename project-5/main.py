# project: p5
# submitter: rarora23
# partner: none
# hours: 45

import sys
import csv
import netaddr
import time
import json
from zipfile import ZipFile
from io import TextIOWrapper
import re
import geopandas
import matplotlib.pyplot as plt


def ip_check(ips):
    file = "ip2location.csv"
    ip_check_list = []
    with open(file, "rb") as f:
        csv_reader =  csv.reader(TextIOWrapper(f))
        header = next(csv_reader) #skip header
        csv_data = [row for row in csv_reader]
    currLine = 0
    for ip in ips:
        t_start = time.time()
        int_ip = int(netaddr.IPAddress(ip))
        left = 0
        right = len(csv_data) - 1
        while left <= right:
            mid = (left + right) // 2
            
            low = int(csv_data[mid][0])
            high = int(csv_data[mid][1])
            region = csv_data[mid][3]
            if int_ip < low:
                right = mid - 1
            elif int_ip > high:
                left = mid + 1
            elif int_ip >= low and int_ip <= high:
                t_end = time.time()
                dur = (t_end - t_start)*1e3
                ip_dict = {
                    "ip" : ip,
                    "int_ip" : int_ip,
                    "region" : region,
                    "ms" : dur
                }
                ip_check_list.append(ip_dict)
                break;
            currLine += 1
    return json.dumps(ip_check_list, sort_keys = 2, indent = 2)


def zip_csv_iter(name, stride=1):
    with ZipFile(name) as zf:
        with zf.open(name.replace(".zip", ".csv")) as f:
            reader = csv.reader(TextIOWrapper(f))
            i = -1
            for row in reader:
                if i%stride  == 0 or i == -1:
                    yield row
                i += 1

def ip_to_int(ip):
    return int(netaddr.IPAddress(ip))

def sort_rows(row):
    ip = re.sub(r"[a-zA-Z]", "0", row[0])
    return ip_to_int(ip)

def sample(inZip, outZip, stride):
    reader = zip_csv_iter(inZip,stride)
    header = next(reader)
    header.append("region") #add region column
    rows = []
    ips = []
    for row in reader:
        ip = row[0]
        ip = re.sub(r"[a-zA-Z]", "0", ip) #remove letters from ip
        ips.append(ip)
        rows.append(row)
    rows = sorted(rows, key=sort_rows)
    ips =  sorted(ips, key=ip_to_int)
    ip_check_out = ip_check(ips)
    ipInfo_list = json.loads(ip_check_out)
    for ip_dict, row in zip(ipInfo_list,rows) :
        row.append(ip_dict["region"]) #add region to the rows
    
    #write to output zip
    with ZipFile(outZip, "w") as zf:
        with zf.open(outZip.replace(".zip", ".csv"), "w") as raw:
            with TextIOWrapper(raw) as f:
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow(header) # write the row of column names to zip2
                for row in rows:
                    writer.writerow(row) # write a row to zip2
        
def world(inZip, outSVG):
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    world = world.loc[world['continent'] != "Antarctica"] #remove antarctica
    world["request_count"] = 0
    reader = zip_csv_iter(inZip)
    regions = {}
    heder = next(reader)
    for row in reader:
        region = row[-1]
        regions[region] = regions.get(region,0) + 1
    for k,v in regions.items():
        world.loc[world['name'] == k, 'request_count']  = v
    fig, ax = plt.subplots(1, 1, figsize=(12,4))
    plt.subplots_adjust(left=0.1, right=0.7)
    world.plot(column = "request_count", ax = ax, legend = True, scheme = "natural_breaks")
    ax.set_title("Web Requests")
    legend = ax.get_legend()
    legend.set_bbox_to_anchor((1.3, 0.7, 0,0))
    plt.savefig(outSVG)
    
        
def main():
    if len(sys.argv) < 2:
        print("usage: main.py <command> args...")
    elif sys.argv[1] == "ip_check":
        ips = sys.argv[2:]
        if len(ips) == 0:
            print("usage: main.py ip_check <IP ADDR 1> <IP ADDR 2> ...")
        else:
            ip_check_out = ip_check(ips)
            print(ip_check_out)
    elif sys.argv[1] == "sample":
            sample_args = sys.argv[2:]
            if len(sample_args) != 3:
                print("usage: main.py sample <INPUT ZIP> <OUTPUT ZIP> <STRIDE>")
            else:
                input_zip = sys.argv[2]
                output_zip = sys.argv[3]
                stride = int(sys.argv[4])
                sample(input_zip, output_zip, stride)
    elif sys.argv[1] == "world":
            world_args = sys.argv[2:]
            if len(world_args) != 2:
                print("usage: main.py world <INPUT ZIP> <OUTPUT SVG IMAGE>")
            else:
                inZip = sys.argv[2]
                outSVG = sys.argv[3]
                world(inZip, outSVG)
    elif sys.argv[1] == "phone":
        phone(sys.argv[2])
        
    else:
        print("unknown command: "+sys.argv[1])
             
def phone(filename):
    num_list = []
    with ZipFile(filename) as zf:
        for info in zf.infolist():
            with zf.open(info.filename, "r") as f:
                tio = TextIOWrapper(f)
                txt = tio.read()
                nums = re.findall(r"[(]\d{3}[)]\s\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|[(]\d{3}[)]\d{3}-\d{4}|\d{3}\s\d{3}-\d{4}",txt)
                for num in nums:
                    if num not in num_list:
                        num_list.append(num)
    for num in set(num_list):
        print(num)
        
         
if __name__ == '__main__':
     main()