#%%
from ftplib import FTP
import json
import sys
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime as dt
import pandas as pd
os.chdir("C:\\Users\\u0136211\\Documents\\GitHub\\LGDF-Asset-Overview-Import\\")
#%%
#This first part sets up the variables, such as FTP credentials and the feed specifics
mode = input("Use config file? (Y/N) ")
if mode == "Y":
    with open('config.json', 'r') as config:
        data = json.load(config)
        ftp_site = data["ftp"]["site"]
        user = data["ftp"]["user"]
        password = data["ftp"]["password"]
        feed_series = data["feed"]["series"]
        feed_seq = data["feed"]["sequence"]
        feed_type = data["feed"]["type"]
        temp = data["temp"]
        log = data["log"]
else:
    data_dict = {}
    temp = input("Where would you like to use as your temp folder: ")
    data_dict["temp"] = temp
    log = input("Where would you like to use as your log file: ")
    data_dict["log"] = log
    data_dict["ftp"] = {}
    ftp_site = input ("Please enter the FTP site address: ")
    data_dict["ftp"]["site"] = ftp_site
    user = input("Please enter your FTP user name: ")
    data_dict["ftp"]["user"] = user
    password = input("Please enter your FTP password: ")
    data_dict["ftp"]["password"] = password
    data_dict["feed"] = {}
    feed_series = input("Please enter the feed series to be downloaded: ")
    data_dict["feed"]["series"] = feed_series
    feed_seq = input("Please enter the last processed sequence: ")
    data_dict["feed"]["sequence"] = int(feed_seq)
    feed_type = input("Please enter the type of feed: ")
    data_dict["feed"]["type"] = feed_type
    with open('config.json', 'w') as config:
        json.dump(data_dict, config)
    
#%%
ftp = FTP(ftp_site, user, password)
open(log, 'a').write(str(dt.utcnow().strftime("%d-%m-%Y %H:%M")) + "\t FTP \t Logged in to " + ftp_site +"\n")
folder_contents = list(ftp.mlsd())

#We then check for md5 checksum files, the last file to be delivered in LGDF deliveries, and create a list of batches to be processed
batches_to_process = []
for item in folder_contents:
    file_name = item[0]
    if not file_name.endswith(".md5"): continue
    if not file_name.split("_")[0] == feed_series: continue
    if not int((file_name.split("_")[3]).split(".")[0]) > feed_seq: continue
    if not file_name.split("_")[1] == feed_type: continue
    batch = file_name.split(".")[0]
    print(batch)
    batches_to_process.append(batch)
if len(batches_to_process) == 0: sys.quit()
batches_to_process = sorted(batches_to_process)

#%%
#This next part downloads each of the zip files for each of the batches in turn, unzipping them, parsing their contents before writing them to a database
names = []

for batch in batches_to_process:
    for file in folder_contents:
        file_name = file[0]
        if not file_name.startswith(batch): continue
        if not file_name.endswith(".zip"): continue
        if file[1]["size"] == 0:
            open(log, 'a').write(str(dt.utcnow().strftime("%d-%m-%Y %H:%M")) + "\t ERROR \t 0 byte file: " + file_name +"\n")
            continue
        local_filename = os.path.join(temp, file_name)
        f = open(local_filename, 'wb')
        ftp.retrbinary('RETR ' + file_name, f.write, 262144)
        open(log, 'a').write(str(dt.utcnow().strftime("%d-%m-%Y %H:%M")) + "\t FTP \t Downloaded " + file_name +"\n")
        f.close()
        for zipfilename in os.listdir(temp):
            if not (zipfile.is_zipfile(temp+ '\\' + zipfilename)): continue
            print(('Unzipping ' + temp + '\\' + zipfilename))
            zipfile.ZipFile(temp+ '\\' + zipfilename).extractall(path=temp)
            os.remove(temp+ '\\' + zipfilename)
            for filename in os.listdir(temp):
                if not filename.endswith('.xml'): 
                    continue
                if filename.startswith("1"):
                    os.remove(temp+ '\\' + filename)
                    continue
                print('Processing ' + filename)
                tree = ET.parse(temp+ '\\' + filename)
                root = tree.getroot()
                ns = str('{http://schemas.thomsonreuters.com/2012/06/30/df5v1.0}')
                parent_id = root.find("./"+ns+"AssetOverview").get("Id")
                share_classes = root.find("./"+ns+"AssetOverview/"+ns+"ShareClasses")
                for share_class in share_classes.iter("ShareClass"):
                    lipper_id = share_class.get("Id")
                    names = share_class.find("./"+ns+"Profile/"+ns+"Names")
                    for name in names.iter("Name"):
                        name_type = name.get("Type")
                        fund_name = name.find("./"+ns+"Text[@Language='ENG']").text
                        current_names = (lipper_id, name_type, fund_name)
                        names.append(current_names)
                os.remove(temp+ '\\' + filename)
            names_df = pd.DataFrame.from_records(names, columns=["Lipper ID", "Name Type", "Name"])
            print(names_df)
    