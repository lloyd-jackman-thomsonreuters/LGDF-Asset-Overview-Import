from ftplib import FTP
import json

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
else:
    data_dict = {}
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
    

ftp = FTP(ftp_site, user, password)
folder_contents = ftp.mlsd()

#We then check for md5 checksum files, the last file to be delivered in LGDF deliveries
for item in folder_contents:
    file_name = item[0]
    if not file_name.endswith(".md5"): continue
    if not file_name.split("_")[0] == feed_series: continue
    if not int((file_name.split("_")[3]).split(".")[0]) > feed_seq: continue
    if not file_name.split("_")[1] == feed_type: continue
    print(file_name)