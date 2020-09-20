import requests
import re
import os
import sys
import getopt
import csv
import time
from requests_html import HTMLSession

# The main function of the script.
# This function will check if the given url is valid.
# Will find all the links on the page.
# Use other function to download the url, calculate ratio and make csv file.
# parameters:
# parent_url - will be used to find the father directory.
# url - the url which been processed.
# depth - the depth value.
# depth_count - counter which will count the depth (for the csv file).
def fetch(parent_url,url,depth=1,depth_count=1):
    # Checking if url is vaild
    if depth == 0:
        print ("minimum depth is 1.")
        exit()
    
    # Checking if we can access the given url. Checkin http and https.
    try:
        info = requests.get(url)
    except:
        try:
            if url.find("https") == 0:
                url = url.replace("https","http")
            else:
                url = url.replace("http","https")
            info = requests.get(url)
        except:
            print("url is not valid")
            return
    
    # Checking the MIME type
    if info.headers.get('content-type') != 'text/html':
        print("MIME type is not text/html")
        return
    else:
        print("MIME type is text/html")
        disk_download(parent_url, info)
        
        # Getting all the links from the url page. 
        print("Finding all the links on" , url)
        session = HTMLSession()
        response = session.get(url)
        links = response.html.absolute_links
        print("Checking url links ratio...")
        ratio = page_ratio(url, links)
        print("Saving the results to a csv file locate in: C:/temp/url_info.csv")
        csv_row = [url,depth_count,ratio]
        csv_outfile(csv_row)
        
        # Running on the links we found from the given url if 
        # the depth is higher then 1.
        if depth > 1:
            for link in links:
                print("\nWorking on link:", link)
                fetch(url,link,depth-1,depth_count+1)
        else: 
            return 

# This function responsible to create the basic directories,
# to create url directory and downloading its html.
# Also this function will check if the url page has updated and 
# if so it will redonwload the page.
# parameters:
# parent_url - url which help to find the father directory.
# info - varible which hold the url content.
def disk_download(parent_url, info):
    file_name = "main.html"
    url = info.url
    # Setting basic directory if needed
    if os.path.exists("C:\\temp\\links"):
        pass
    else:
        if os.path.exists("C:\\temp"):
           os.mkdir("C:\\temp\\links")
        else:
            os.mkdir("C:\\temp")
            os.mkdir("C:\\temp\\links")
    # Getting the parent directory path. 
    if parent_url != None:
        parent_dir = parent_url.split("//")[1]
        parent_dir = re.sub('[^a-zA-Z0-9\.]', '-', parent_dir)
        for roots,dirs,files in os.walk("C:\\temp"):
            if parent_dir in dirs:
                path = roots + "\\" + parent_dir
    else:
        path = "C:\\temp\\links" 

    # Setting the dir url withour special charecters           
    dir_name = url.split("//")[1]
    dir_name=re.sub('[^a-zA-Z0-9\.]', '-', dir_name)
    dir = os.path.join(path,dir_name)
    
    # Checking we already downloaded the url
    if not os.path.exists(dir):
        print ("Saving the content of the url to a file")
        os.mkdir(dir)
        file_location = os.path.join(dir,file_name)
        with open(file_location,'w', encoding="utf-8") as inputfile:
            inputfile.write(info.text)
        return
    else:
        print("The url already downloaded\nChecking if the page has modifide...")
        file_location = os.path.join(dir,file_name)
        file_status = os.stat(file_location)
        if time.ctime(file_status.st_mtime) < info.headers.get('last-modified'):      
            print("The website has updated...\nUpdate html...")
            with open(file_location,'w', encoding="utf-8") as inputfile:
                inputfile.write(info.text)
        else:
            print("The page is uptodate")
        return

def page_ratio(url,links):
    domain = url.split('/')[2]
    count = 0
    domain_count = 0
    for link in links:
        if link.split('/')[2] == domain:
            domain_count += 1
            count += 1
        else:
            count += 1
    return round(domain_count/count,2)

def csv_outfile(csv_row):
    csv_file_path = "C:\\temp\\url_info.csv"
    header = ["url","depth","ratio"]
    if os.path.exists(csv_file_path):
        try:
            with open('C:\\temp\\url_info.csv','a', newline='') as csv_outfile:
                csv_writer = csv.writer(csv_outfile)
                csv_writer.writerow(csv_row)
        except Exception as e:
            print(e)
            exit()
    else: 
        try:
            with open('C:\\temp\\url_info.csv','w', newline='') as csv_outfile:
                csv_writer = csv.writer(csv_outfile)
                csv_writer.writerow(header)
                csv_writer.writerow(csv_row) 
        except Exception as e:
            print(e)
            exit()
            
def main ():
    url_list = list()  
    argv = sys.argv[1:]
    
    # Checking if the user enterd the right parameters.
    try: 
        opts, args = getopt.getopt(argv,"u:d:h",["urls =", "depth ="])   
    except: 
        print("Enter valid parameters") 
        
    # Setting command line parameters
    for opt, arg in opts: 
        print(opt,arg)
        if opt in ['-u', '--urls']: 
            urls = arg 
        elif opt in ['-d', '--depth']: 
            depth = int(arg)
        elif opt in ['-h']:
            print("-u <urls> -d <depth> -h <help>")
            exit()
    try:    
        urls
    except NameError:
        print("Don't forget to use '-u' in order to enter urls.")
    
    # Setting url list and start to run on the given urls.
    url_list.extend(urls.split(','))
    for url in url_list:
        parent_url = None # Setting the parent url to none in the first run.
        if url.find("http") < 0 :
            url = "https://" + url
        print("\nWorking on url:",url)
        fetch(parent_url,url,depth)
               
main()