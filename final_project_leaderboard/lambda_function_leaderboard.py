#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import re
import logging
import boto3
import os

credentials_profile_name = "default"
region_name = "us-east-1"

# setting logger
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_answer(text):
    print(f"Entered extract_answer with input >>>>>>> {text}")
    extracted_answer = text
    '''
    # Pattern to find "Answer *** Number"
    pattern1 = r".*[aA]nswer.*?(\d+)"
    # Pattern to find the last number in a string
    # https://stackoverflow.com/questions/5320525/regular-expression-to-match-last-number-in-a-string
    #pattern2 = r"(\d+)(?=\D*$)"
    # Try with first pattern
    match = re.findall(pattern1, text, re.DOTALL)
    if match:
        extracted_answer = int(match[0])
        print(f"Answer after pattern 1 >>>>>>> {extracted_answer}")
    
    else:
        # Try with second pattern
        match = re.findall(pattern2, text, re.DOTALL)
        if match:
            extracted_answer = int(match[0])
    print(f"Entered extract_answer response after pattern 2>>>>>>> {extracted_answer}")
    '''
    rsp =  {
        "response": 
            {
                "leaderboardAnswer": str(extracted_answer).upper()
            }
    }
    print(f"rsp >>>>>>> {rsp}")
    return rsp


def lambda_handler(event, context):
    print("Entered lambda_handler >>>>>>> ")
    print(f"event >>>>> {event}")
     
    action = event['actionGroup']
    api_path = event['apiPath']
    llm_answer = event['requestBody']['content']['application/json']['properties'][0]['value']
    print(f"llm_answer RAW >>>>> {llm_answer}")
    if api_path == '/parse-kbresult':
        print("Calling main_run_query_empty() >>>>>>> ")
        body = extract_answer(llm_answer)
        print(f"body after extract_answer>>>>>>> {body}")
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

