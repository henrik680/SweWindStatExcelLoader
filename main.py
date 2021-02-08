import pandas as pd
import re
import requests
import logging
from google.cloud import storage
from google.cloud.storage import Blob

def openExcelUrl(url):
    s = requests.get(url).content
    return openExcel(s)

def openExcel(file_or_content):
    df = pd.read_excel(file_or_content,
                       engine='openpyxl',
                       skiprows=4)
    logging.debug("openExcel(...): pandas dataframe from excel top 10:{}".format(df.head(10)))
    return df


def legacy_remove_mid_newlines(csv):
    # Swedish renewable energy excel file has new line in the middle of column headers

    iter_max = 1
    first_pos = csv.find('"')
    if first_pos > 0: found=True
    new_csv = csv[:first_pos]
    while found > 0 and iter_max < 100:
        second_pos = csv[first_pos+1:].find('"') + first_pos+1
        new_csv += csv[first_pos:second_pos+2].replace('\n','')
        first_pos = csv[second_pos+1:].find('"') + second_pos+1
        if first_pos==second_pos: found=False
        iter_max += 1
    new_csv += csv[second_pos+1:]
    return new_csv

def remove_mid_newlines(csv):
    # Swedish renewable energy excel file has new line in the middle of column headers
    (csv_new,csv_new_array,latest_end) = ('',[],0)
    for match in re.compile('\"(.|\n)*?\"').finditer(csv):   # non greedy over carriage return line feed
        latest_start = match.start()
        csv_new_array.append(csv[latest_end:latest_start])
        csv_new_array.append(match.group().replace('\n',''))
        latest_end = match.end()
    csv_new_array.append(csv[latest_end:])
    for s in csv_new_array:
        csv_new += s
    return csv_new


def upload_blob_string(bucket_name, csvString, destination_blob_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = Blob(destination_blob_name, bucket)
    return blob.upload_from_string(
        data=csvString,
        content_type='text/csv')


def run(request):
    logging.info("Starting SweWindStatExcelLoader")
    file_name = ''
    #file_name = '/Users/henrik/data/Godkända anläggningar_14cols50rows.xlsx'
    #file_name = '/Users/henrik/data/Godkända anläggningar_5cols15rows.xlsx'
    #file_name = '/Users/henrik/data/Godkända anläggningar_2cols3rows.xlsx'
    if file_name is not '':
        logging.info("Excel File=" + file_name)
        df = openExcel(file_name)
    else:
        fileUrl = "http://epi6.energimyndigheten.se/SharePoint/Eugen/Godkända anläggningar.xlsx"
        logging.info("URL=" + fileUrl)
        df = openExcelUrl(fileUrl)
    csvString = remove_mid_newlines(df.dropna(axis='columns').to_csv(index=False)) # Dropping empty column
    bucket_name = "swe-renew-energy-stat"
    destination_blob_name = "blob-csv"
    upload_blob_string(bucket_name, csvString, destination_blob_name)
    logging.info("Uploaded size={} to bucket {} and {}".format(df.size,bucket_name,destination_blob_name))


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run(234)