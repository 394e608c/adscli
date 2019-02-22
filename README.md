Adobe Data Sources CLI
====================

A simple CLI wrapper for the Adobe Analytics Data Sources API

## Motivation
It is critical for analysts to be able to consume, analyze, and visualize all of their marketing data in one place, and Adobe's data sources API is a powerful tool to help import and merge disparate marketing data for use in the Analytics tool. However, it's not always clear how to get started and use the API, so I wanted to build a simple interface that allows beginners/non-technical users to start managing and importing 3rd party data into Adobe Analytics.

## Documentation
* [Adobe Data Sources GitHub](https://github.com/AdobeDocs/analytics-1.4-apis/blob/master/docs/data-sources-api/c_data_sources_api_1_4.md)
* [Adobe Data Sources User Guide (PDF)](https://marketing.adobe.com/resources/help/en_US/sc/datasources/adobe_analytics_data_sources.pdf)
* [Adobe Data Sources Help](https://marketing.adobe.com/resources/help/en_US/sc/datasources/)


![data sources](https://marketing.adobe.com/resources/help/en_US/sc/datasources/graphics/data_sources_overview.png)

## Installation
```
$ git clone https://github.com/394e608c/adscli.git
$ cd adscli
$ pip install -r requirements.txt
$ cd scripts
```

## Authentication

*Note - now that Adobe has rolled out Service Account Integration and OAuth integration via the [new console](https://console.adobe.io/integrations), I'll be looking to add additional authentication methods in the near future.*

You need to generate a client id and client secret via Adobe's *Legacy OAuth Applications*:

1. Log in to Adobe Analytics
2. Admin > User Management (Legacy)
3. Click to Legacy OAuth Applications tab
4. Add application
5. Give it a name and select 'Data Sources' under Scopes

Next, open config.txt and paste your id/secret:

```
[CONFIG]
client_id = *paste client id here*
client_secret = *paste client secret here*
grant_type = client_credentials
```

## Supported Methods
1. [DataSources.Get](#datasourcesget)
2. [DataSources.Delete](#datasourcesgdelete)
3. [DataSources.GetJobs](#datasourcesgetjobs)
4. [DataSources.UploadData](#datasourcesuploaddata)


## DataSources.Get
Returns list of data sources. Simply pass in a reposrt suite ID with --rsid.

#### Usage:
```
$ python get_sources.py --rsid=mytestreportsuite
```

```
python get_sources.py --help

Options:
  --rsid TEXT  The report suite ID  [required]
  --help       Show this message and exit.
```

### Response:
```
{
    "id": int,
    "processing_type": string,
    "name": string,
    "email": string,
    "activatedDate": date,
    "ftp": {
      "path": string,
      "loginID": string,
      "password": string
    },
    "haltOnWarning": boolean,
    "haltOnError": boolean,
    "lockedByError": boolean 
  }
```


## DataSources.Delete
Deletes a given data source. Pass in report suite ID (--rsid) and a data soure ID to delete (--dsid)
#### Usage:
```
$ python delete_source.py --rsid=mytestreportsuite --dsid=2
```
```
python delete_source.py --help

Options:
  --dsid TEXT  The dataSourceID  [required]
  --rsid TEXT  The report suite ID  [required]
  --help       Show this message and exit.
```
You will be prompted to confirm before actually making the request to delete the source:

```
You are about to permenantly delete dataSourceID: 2. Are you sure you want to proceed? [y/N]: 
```

### Response:

```
Data source 2 successfully deleted
```
## DataSources.GetJobs
Returns a list of every job run for a particular data source. Pass in report suite ID (--rsid) and a data soure ID (--dsid)

#### Usage:
```
$ python get_jobs.py --rsid=mytestreportsuite --dsid=2
```

```
python get_jobs.py --help

Options:
  --dsid TEXT  The dataSourceID  [required]
  --rsid TEXT  The report suite ID  [required]
  --help       Show this message and exit.
```

### Response:
```
[
  {
    "id": int,
    "fileName": string,
    "startDate": date,
    "finishDate":date,
    "size": int,
    "rows": int,
    "errors": [],
    "warnings": [],
    "receivedDate": date,
    "status": string
  }
]
2 jobs found for dataSourceID 2
```

## DataSources.UploadData
Uploads data to a particular data source. Per usual, pass in a report suite ID (--rsid) and a data soure ID (--dsid).Additional required fields:

* --job-name: A name for the job (will be used in the fileName field in the response from GetJobs)
* --file: The path of a valid CSV with your data to load (no column headers)
* --cols: A comma delimited list (wrapped in quotes) of columns which should match the column names of you data source. Example: 'Event 1,Event 5,Evar 20'

**Important**: The order of column headers passed with --cols MUST match the order of the columns in your CSV to load. If --cols='Event 1,Event 5,Evar 20', then your CSV should have event1 in col A, event5 in col B and evar20 in col C.

#### Usage:
```
$ python upload_data.py --rsid=mytestreportsuite --dsid=2 --columns=Event 1,Evar 30 --file=file_to_load.csv --job-name=test
```

```
python upload_data.py --help

  --job-name TEXT  A name for the job  [required]
  --cols TEXT      Provide a column delimited list of column names (Ex: 'Evar 1,Event 1')  [required]
  --file TEXT      Provide the path for a CSV  [required]
  --dsid TEXT      The dataSourceID  [required]
  --rsid TEXT      The report suite ID  [required]
  --help           Show this message and exit.
```

You will be prompted to confirm before actually making the request to POST the data:

```
Data is formatted and ready to load. Would you like to proceed? [y/N]: 
```

### Response:
```
Data successfully loaded!
```