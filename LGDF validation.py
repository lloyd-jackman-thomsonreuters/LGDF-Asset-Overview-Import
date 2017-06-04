import sys
import os
from lxml import etree
from ftplib import FTP
import zipfile

def validate(xmlparser, xmlfilename):
    try:
        with open(xmlfilename, 'rb') as f:
            etree.fromstring(f.read(), xmlparser)
        return True
    except etree.XMLSchemaError:
        return False

os.chdir("C:\\Users\\u0136211\\Documents\\LGDF Validation\\")
dwnld = "C:\\Users\\u0136211\\Documents\\LGDF Validation\\"

#schema_file = "C:\\Users\\u0136211\\Documents\\Df5Schema-v13.xsd"
#schema_file = "C:\\Users\\u0136211\\Documents\\Df5Schema 18.xsd"
schema_file = "C:\\Users\\u0136211\\Documents\\Df5Schema 18 test.xsd"

with open(schema_file, 'rb') as f:
    schema_root = etree.XML(f.read())

schema = etree.XMLSchema(schema_root)
xmlparser = etree.XMLParser(schema=schema)
results = {}
"""
open("LGDF validation.txt", "w")
open("LGDF validation.txt", "w").close()

open("LGDF validation - error details.txt", "w")
open("LGDF validation - error details.txt", "w").close()
"""
already_done = []
for line in open("LGDF validation.txt"):
	already_done.append(line.split("\t")[0])
#print(len(already_done))

#ftp = FTP('lipperftp.thomsonreuters.com', user, password)
#ftp.cwd('/datafeeds/LipperGlobalDataFeed5/standardfeed/')
ftp = FTP('ftp2.lipper.reuters.com', user, password)
ftp.cwd('/datafeeds/LipperGlobalDataFeed5/lipperinternal/')
for line in ftp.mlsd(facts=['modify']):
	print(line)
	file = line[0]
	if not (file.endswith(".zip")): continue
	#if not file.split('_')[5] == "INC.zip": continue
	if not file.split('_')[1] == "LGDF": continue
	if not file.split('_')[0] == "oztest": continue
	#if not int(file.split('_')[2]) >= 20170424: continue
	if file in already_done: continue
	print('Downloading ' + file)
	local_filename = os.path.join(dwnld, file)
	f = open(local_filename, 'wb')
	ftp.retrbinary('RETR ' + file, f.write, 262144)
	f.close()
	for zipfilename in os.listdir(dwnld):
		if not (zipfile.is_zipfile(dwnld+ '\\' + zipfilename)): continue
		results[zipfilename] = {}
		results[zipfilename]["Pass"] =  0
		results[zipfilename]["Fail"] =  0
		zipfilecontents = zipfile.ZipFile(dwnld + '\\' + zipfilename).namelist()
		for xmlfile in zipfilecontents:
			if not xmlfile.endswith(".xml"): continue
			try:
				zipfile.ZipFile(dwnld + '\\' + zipfilename).extract(xmlfile)
				validate(xmlparser, xmlfile)
				#print(xmlfile + " correctly validated")
				results[zipfilename]["Pass"] += 1
			except:
				print(xmlfile + " failed validation\t" + (".").join(str(sys.exc_info()[1]).split(".")[:-1]))
				open("LGDF validation - error details.txt", "a").write(xmlfile + "\t" + (".").join(str(sys.exc_info()[1]).split(".")[:-1])+"\n")
				results[zipfilename]["Fail"] += 1
			try:
				os.remove(xmlfile)
			except:
				pass
		if results[zipfilename]["Fail"] == 0:
			pass_rate = 100
		elif results[zipfilename]["Pass"] == 0:
			pass_rate = 0
		else:
			pass_rate = round((1-(results[zipfilename]["Fail"]/(results[zipfilename]["Fail"]+results[zipfilename]["Pass"])))*100,2)
		open("C:\\Users\\u0136211\\Documents\\LGDF Validation\\LGDF validation.txt", "a").write(zipfilename + "\tPass rate:\t" + str(pass_rate)+"%\n")
		os.remove(dwnld+ '\\' + zipfilename)
ftp.quit()
open("C:\\Users\\u0136211\\Documents\\LGDF Validation\\LGDF validation.txt", "a").close()
open("LGDF validation - error details.txt", "a").close()
