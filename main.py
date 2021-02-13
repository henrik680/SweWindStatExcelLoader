import pandas as pd
import re
import requests
import logging
import json
import argparse
from google.cloud import storage
from google.cloud.storage import Blob


logging.getLogger().setLevel(logging.INFO)


def open_excel_url(url):
    logging.info("openExcel(...): url={}".format(url))
    s = requests.get(url).content
    return open_excel(s)


def open_excel(file_or_content):
    df = pd.read_excel(file_or_content,
                       engine='openpyxl',
                       skiprows=4)
    logging.debug("openExcel(...): pandas dataframe from excel top 10:{}".format(df.head(10)))
    return df


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
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='json with parameters')
    args = parser.parse_args()
    logging.info('run(...): requestr={}'.format(request))
    logging.info('run(...): args={}'.format(args))
    if request == None:
        logging.info('run(...): data=' + args.data)
        input_json = json.loads(str(args.data).replace("'",""))
    else:
        input_json = request.get_json()

    logging.info("request.args: {}".format(input_json))
    bucket_name = input_json['bucket_target']
    file_location = input_json['file_location']
    destination_blob_name = input_json['destination_blob_name']
    logging.info("\nbucket_name: {}\nfile_location: {}\ndestination_blob_name: {}".format(
        bucket_name, file_location, destination_blob_name))

    if file_location.startswith('http'):
        logging.info("run(...) URL=" + file_location)
        df = open_excel_url(file_location)
    else:
        logging.info("run(...) Excel File=" + file_location)
        df = open_excel(file_location)
    csvString = remove_mid_newlines(df.to_csv(index=False, sep=';')) # Dropping empty column
    upload_blob_string(bucket_name, csvString, destination_blob_name)
    logging.info("Uploaded size={} to bucket {} and {}".format(df.size,bucket_name,destination_blob_name))


if __name__ == '__main__':
    run(None)