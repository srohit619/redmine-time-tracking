## Redmine Time Track
![Static Badge](https://img.shields.io/badge/Release-v1.0-green) 
![Static Badge](https://img.shields.io/badge/Language-Python-blue)

### SLA Report Specification

1. **Month/Quarter** : The SLA module provides metrics for both monthly and quarterly reporting.

2. **Severity** : Severity levels are categorized as follows:
   - Severity 1 & 2: High and Showstopper
   - Severity 3 & 4: Medium and Low
   

3. **Total** : The module calculates the total count of issues falling under the selected month/quarter and severity level.

4. **SLA Past Count**: This metric tracks the number of SLA failures for issues falling under the selected month/quarter and severity level. SLA thresholds are defined as follows:
   - Severity 1 & 2: 2 hours
   - Severity 3 & 4: 720 hours (30 days)

5. **SLA Meet** : This metric represents the pass percentage of SLA compliance and is calculated using the formula: `(Total - SLA Past Count) / Total`.

6. **Goal** : SLA compliance goals are set as follows:
   - Severity 1 & 2: 95%
   - Severity 3 & 4: 80%

7. **Goal Met** : A binary indicator that shows whether SLA compliance goals have been met. If `SLA Meet > Goal`, it is marked as 'Y' (Yes); otherwise, it is marked as 'N' (No).


### Configuring the Redmine Time-Tracker

* Make sure Pyhton is installed on your server
* Get the API KEY from your Redmine
    * On Redmine click My Account and on the left side you will find API Key  
* Get the Project ID of which you want to extract data
    *  Goto https://<<redmine_api>>/projects.json and search the project and copy paste the Project ID into the config.json file.
* Extract the zip file (redmine-time-track)
* Navigate to config folder and open config.json and then add or modify the following changes 


### For Configuring this with your project can be done via the config.json file below are the details:**

| Name | Value | Description |
|---|---|---|
|csv_path|./csv/|Path in which you want the CSV to be Generated |
|project_id|<<PROJECT_CODE>>|Project Id of the Project which you want to get the details for|
|redmine_url|<<YOUR_REDMINE_URL>> | URL of the Redmine, There are different URLs for Redmine according to Vendor|
|api_token|<<YOUR_API_KEY_API>> | Key of the User using which we will pull the data from Redmine |
|csv_output_name|detailed.csv or summary-Month.csv |This will be used as file name, Output CSV Names|
|severnity|1,2,3,4|Prioritywise Count from low to showstopper |
|goal|95 for one_and_two and 80 for three_and_four |Goals include Hours , one and two = 95 hours, so and so |

### After Setup 

Go to the Extracted Directory and fire the below command
```
py app.py
```

> the process will start and the csv files will be generated in CSV folder and this process takes time according to the project issues

