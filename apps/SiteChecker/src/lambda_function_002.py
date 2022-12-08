import boto3
import csv
import gzip
import http
import json
import os
import ssl

from datetime import datetime



def get_site_data(conn, http_method, url, site, port):
    try:
        conn.request(http_method, url)
    except Exception as err:
        result = {'lambda_status': 'ERROR', 'site': site, 'port': port, 'message': str(err)}
    else:
        result = {'lambda_status': 'Completed', 'site': site, 'port': port, 'message': None, 'status': response.status, 'reason': response.reason}
    finally:
        print(json.dumps(result))
    return result


def lambda_handler(event, context):
    print(json.dumps(event))

    today = datetime.today().strftime('%Y/%m/%d')
    now = datetime.today().utc().strftime('%Y-%m-%dT%H:%M:%SZ')

    with gzip.open('/tmp/results.csv.gz', 'wt', newline='') as csvfile:
        fieldnames = ['id', 'lambda_status', 'site', 'port', 'message', 'status', 'reason']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        counter = 1
        for record in event['Records']:
            site = record['body']
            print(json.dumps({'lambda_status': 'Information', 'site': site, 'message': None}))

            try:
                conn = http.client.HTTPConnection(site, 80, timeout=1)
            except Exception as err:
                result = {'lambda_status': 'ERROR', 'site': site, 'port': 80, 'message': str(err)}
                print(json.dumps(result))
            else:
                result = get_site_data(conn, 'GET', '/', site, 80)
            finally:
                result['id'] = counter
                writer.writerow(result)
                counter += 1

            try:
                conn = http.client.HTTPSConnection(site, 443, timeout=1, context=ssl._create_unverified_context())
            except Exception as err:
                result = {'lambda_status': 'ERROR', 'site': site, 'port': 443, 'message': str(err)}
                print(json.dumps(result))
            else:
                result = get_site_data(conn, 'GET', '/', site, 443)
            finally:
                result['id'] = counter
                writer.writerow(result)
                counter += 1

    # Push to S3
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('your-bucket-name')
    key = f'sitechecker/{today}/siteresults_{now}.csv.gz'
    bucket.upload_file('/tmp/results.csv.gz', key)
    return