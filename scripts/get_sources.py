import configparser
import logging
import json
import requests
import click

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
  body = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': GRANT_TYPE}
  
  r = requests.post(endpoint, data=body)

  resp = r.json()
  status_code = r.status_code
  err_msg = 'Problem retrieving token'

  # if the rquest is good, return the token. If not, return a message we can use in main()
  if status_code == 200:
    token = resp['access_token']
    return token
  else:
    return err_msg

# args for our CLI
@click.command()
@click.option('--rsid', required=True, help='The report suite ID')

# takes input from CLI and makes the request
def get_sources(rsid):
  token = get_token()

  # ensure the token is available to be used in our request
  if token == 'Problem retrieving token':
    click.echo(click.style(token, fg='red'))
  else:
    click.echo(click.style('Successfully retrieved Bearer token', fg='green'))

  delete_jobs_endpoint = 'https://api.omniture.com/admin/1.4/rest/?method=DataSources.Get'
  post_body = {"reportSuiteID":rsid}
  headers = {"Authorization":"Bearer "+token, "Content-Type":"application/json"}

  r = requests.post(delete_jobs_endpoint, json=post_body, headers=headers)

  json_resp = r.json()
  output = json.dumps(json_resp, indent=2)
  count = sum(1 for record in json_resp)

  status_code = r.status_code

  if status_code == 200:
    click.echo(output)
    click.echo(click.style('%s sources found' % count, fg='green'))
  else:
    click.echo(click.style('There was a problem getting data sources:', fg='red'))
    click.echo(output)

if __name__ == '__main__':
  get_sources()