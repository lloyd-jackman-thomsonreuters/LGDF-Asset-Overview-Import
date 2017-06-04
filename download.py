from ftplib import FTP
import json

mode = input("Use config file? (Y/N) ")
if mode == "Y":
    with open('config.json', 'r') as config:
        data = json.load(config)
        user = data["ftp"]["user"]
        password = data["ftp"]["password"]
        feed_series = data["feed"]["series"]
else:
    data_dict = {}
    user = input("Please enter your FTP user name: ")
    data_dict["ftp"] = {}
    data_dict["ftp"]["user"] = user
    password = input("Please enter your FTP password: ")
    data_dict["ftp"]["password"] = password
    feed_series = input("Please enter the feed series to be downloaded: ")
    data_dict["feed"] = {}
    data_dict["feed"]["series"] = feed_series
    with open('config.json', 'w') as config:
        data = json.dump(data_dict, config)
    

ftp = FTP("lipperftp.thomsonreuters.com", user, password)
folder_contents = ftp.mlsd()
for item in folder_contents:
    file_name = item[0]
    print(file_name)