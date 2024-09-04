#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import re
import logging
import sqlite3
import boto3
import os

credentials_profile_name = "default"
region_name = "us-east-1"

# setting logger
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


s3 = boto3.client('s3')
bucket = os.environ.get('BUCKET_NAME')  #Name of bucket with data file and OpenAPI file
kb_prefix = os.environ.get('KB_PREFIX')

print(f'bucket :::: {bucket} and kb_prefix :::: {kb_prefix}')
# kb_prefix+'/'+
db_name = 'northwind.db' #Location of data file in S3
local_db = '/tmp/northwind.db' #Location in Lambda /tmp folder where data file will be copied

#Download data file from S3
s3.download_file(bucket, db_name, local_db)

cursor = None
conn = None

#Initial data load and SQLite3 cursor creation 
def load_data():
    #load SQL Lite database from S3
    # create the db
    global conn
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    print('Completed initial Northwind data load ')

    return cursor

def get_named_parameter(event, name):
    return next(item for item in event['parameters'] if item['name'] == name)['value']

def run_query_helper(query):
    try:
        cursor.execute(query)
        resp = cursor.fetchall()
        #adding column names to response values
        col_names = [description[0] for description in cursor.description]
        valDict = {}
        index = 0
        for name in col_names:
            valDict[name]=resp[0][index]
            index = index + 1
        print('Customer Info retrieved')
        return "success", col_names, resp, valDict
    
    except Exception as e:
        return "fail", "", str(e), {} 


def run_query(query):
    status, columns, query_result, valDict = run_query_helper(query)
    print(f"query_result :: {query_result} and valDict :: {valDict}")
    if query_result and status=="success":
        return query_result, valDict


def main_run_query(sql_query):
    print(f"Entered main_run_query_empty >>>>>>> {sql_query}")
    query_result = None
    query_result, valDict = run_query(sql_query)
    print(f"query_result >>>>>>> {query_result} and valDict :: {valDict}")
    rsp =  {
        "response": 
            {
                "generatedSQL": sql_query,
                "query_result": query_result
            }
    }
    
    return rsp


def lambda_handler(event, context):
    print("Entered lambda_handler >>>>>>> ")
    print(f"event >>>>> {event}")
    
    global cursor
    if cursor == None:
        cursor = load_data()
    
    action = event['actionGroup']
    api_path = event['apiPath']
    sql_query = event['requestBody']['content']['application/json']['properties'][0]['value']
    print(f"sql_query >>>>> {sql_query}")
    print(f"cursor >>>>> {cursor}")
    if api_path == '/run-query':
        print("Calling main_run_query_empty() >>>>>>> ")
        body = main_run_query(sql_query)
    else:
        body = {"{}::{} is not a valid api, try another one.".format(action, api_path)}

    response_body = {
        'application/json': {
            'body': str(body)
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    response = {'response': action_response}
    return response

