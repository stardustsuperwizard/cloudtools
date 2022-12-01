import boto3
import datetime
import http
import json
import os
import ssl


def get_site_data(conn, http_method, url, site, port):
    try:
        conn.request(http_method, url)
    except Exception as err:
        print(json.dumps({'lambda_status': 'ERROR', 'site': site, 'port': port, 'message': str(err)}))
    else:
        print(json.dumps({'lambda_status': 'Completed', 'site': site, 'port': port, 'message': None, 'status': response.status, 'reason': response.reason}))
    return


def lambda_handler(event, context):
    print(json.dumps(event))
    for record in event['Records']:
        site = record['body']
        print(json.dumps({'lambda_status': 'Information', 'site': site, 'message': None}))

        try:
            conn = http.client.HTTPConnection(site, 80, timeout=1)
        except Exception as err:
            print(json.dumps({'lambda_status': 'ERROR', 'site': site, 'port': 80, 'message': str(err)}))
        else:
            get_site_data(conn, 'GET', '/', site, 80)

        try:
            conn = http.client.HTTPSConnection(site, 443, timeout=1, context=ssl._create_unverified_context())
        except Exception as err:
            print(json.dumps({'lambda_status': 'ERROR', 'site': site, 'port': 443, 'message': str(err)}))
        else:
            get_site_data(conn, 'GET', '/', site, 443)
    return