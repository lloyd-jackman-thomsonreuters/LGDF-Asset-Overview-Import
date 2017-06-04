from ftplib import FTP
import json

mode = input("Use config file? (Y/N) ")
if mode == "Y":
    with open('config.json') as config:
        data = json.load(config)
        user = data[ftp][user]
        password = data[ftp][password]
else:
    user = input("Please enter your FTP user name: ")
    password = input("Please enter your FTP password: ")
    feed_series = input("Please enter the feed series to be downloaded: ")

ftp = FTP("lipperftp.thomsonreuters.com", user, password)
folder_contents = ftp.mlsd()
for item in folder_contents:
    file_name = item[0]