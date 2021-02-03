import pandas as pd
import requests
from google.cloud import storage
from google.cloud.storage import Blob

def openExcelUrl(url):
    s = requests.get(url).content
    xl = pd.read_excel(s, skiprows=4, engine='openpyxl')
    return xl


def upload_blob_string(bucket_name, csvString, destination_blob_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = Blob(destination_blob_name, bucket)
    blob.upload_from_string(
        data=csvString,
        content_type='text/csv')


def run(request):
    print("Starting SweWindStatExcelLoader")
    fileUrl = "http://epi6.energimyndigheten.se/SharePoint/Eugen/Godkända anläggningar.xlsx"
    print("URL=" + fileUrl)
    df = openExcelUrl(fileUrl)
    csvString = df.to_csv()
    bucket_name = "swe-renew-energy-stat"
    destination_blob_name = "blob-csv"
    upload_blob_string(bucket_name, csvString, destination_blob_name)
    print("Uploaded {} to bucket {} and {}".format(df.size,bucket_name,destination_blob_name))
