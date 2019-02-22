import click
import configparser
import requests
import logging
import urllib
import json
import csv

# logging for debugging outbound requests
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
REQUESTS_LOG = logging.getLogger("requests.packages.urllib3")
REQUESTS_LOG.setLevel(logging.DEBUG)
REQUESTS_LOG.propagate = True

# read in auth parameters from config
CONFIG = configparser.ConfigParser()
CONFIG.read('config.txt')
CLIENT_ID = CONFIG.get('CONFIG', 'client_id')
CLIENT_SECRET = CONFIG.get('CONFIG', 'client_secret')
GRANT_TYPE = CONFIG.get('CONFIG', 'grant_type')

# returns bearer token [expires in 3600s]
def get_token():
  endpoint = 'https://api.omniture.com/token'
  body = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": GRANT_TYPE}
  
  r = requests.post(endpoint, data=body)

  resp = r.json()
  status_code = r.status_code
  err_msg = 'Problem retrieving token'

  # if the request is good, return the token. If not, return a message we can use in main()
  if status_code == 200:
    token = resp['access_token']
    return token
  else:
    return err_msg

# process input file for upload
def process_file(file):
  with open(file, 'r') as f:
    reader = csv.reader(f)
    for record in reader:
      yield json.dumps(record)

# args for our CLI
@click.command()
@click.option('--job-name', required=True, help='A name for the job')
@click.option('--cols', required=True, help='Provide a column delimited list of column names (Ex: "Evar 1,Event 1")')
@click.option('--file', required=True, help='Provide the path for a CSV')
@click.option('--dsid', required=True,  help='The dataSourceID')
@click.option('--rsid', required=True,  help='The report suite ID')

def upload_file(job_name, cols, file, dsid, rsid):
  token = get_token()
  
  # ensure the token is available to be used in our request
  if token == 'Problem retrieving token':
    click.echo(click.style(token, fg='red'))
  else:
    click.echo(click.style('Successfully retrieved Bearer token', fg='green'))


  col_headers = cols.split(',')
  
  # parse csv and comma delimit the fields
  records = process_file(file)
  rows = ','.join(str(a) for a in records)
  
  # format keys/values for POST body
  c = '"{}"'.format("columns")
  c2 = json.dumps(col_headers)

  d = '"{}"'.format("dataSourceID")
  d2 = json.dumps(dsid)

  f = '"{}"'.format("finished")
  f2 = '"{}"'.format("true")

  j = '"{}"'.format("jobName")
  j2 = json.dumps(job_name)

  s = '"{}"'.format("reportSuiteID")
  s2 = json.dumps(rsid)

  w = '"{}"'.format("rows")

  post_body = '{'+c+':'+c2+','+d+':'+d2+','+f+':'+f2+','+j+':'+j2+','+s+':'+s2+','+w+':'+'['+rows+']'+'}'
  endpoint = 'https://api.omniture.com/admin/1.4/rest/?method=DataSources.UploadData'
  headers = {"Authorization":"Bearer "+token, "Content-Type":"application/json"}
  
  # dsid 22 for testing, 'Date,Event 125,Evar 100,Event 126,Event 124,Tracking Code'
  #post_body = {"columns":col_headers,"dataSourceID":dsid,"finished":"true","jobName":job_name,"reportSuiteID":rsid,"rows":rows}

  # confirm before initiating the request
  confirm_msg = click.style('Data is formatted and ready to load. Would you like to proceed?', fg='red')
  click.confirm(confirm_msg, abort=True)

  r = requests.post(endpoint, data=post_body, headers=headers)

  # get response and output result
  resp = r.json()
  output = json.dumps(resp, indent=2)

  if resp == True:
    click.echo(click.style('Data successfully loaded!', fg='green'))
  else:
    click.echo(click.style('Problem loading data:', fg='red'))
    click.echo(output)

if __name__ == '__main__':
  upload_file()

