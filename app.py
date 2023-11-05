import csv
from redminelib import Redmine
import redminelib
from datetime import datetime
import pandas as pd
import os
import json
import time

# Record the start time
start_time = time.time()
print('Execution started')

# Read the CSV path from config.json
with open("./config/config.json", "r") as config_file:
    config_data = json.load(config_file)
    project_id = config_data["project_id"]
    redmine_url = config_data["redmine_url"]
    api_key = config_data["api_token"]
    csv_path = config_data["csv_path"]
    csv_output_name = config_data["csv_output_name"]
    severnity = config_data["severnity"]
    goal = config_data["goal"]

# Initialize Redmine client
redmine = Redmine(redmine_url, key=api_key)

# Project ID (replace with your project's ID)
project_id = project_id


# Fetch issues for the specified project
issues = redmine.issue.filter(project_id=project_id,status_id='*')


statusesin = redmine.issue_status.all()


def statuses(target_id):  
    for status in statusesin:
        if status['_decoded_attrs']['id'] == target_id:
            return status['_decoded_attrs']['name']
    return None  # Return None if no match is found


def get_month(input_date, start_day, first_month):
    current_month = first_month
    for i in range(1, 13):
        if (
            (current_month == input_date.month and start_day <= input_date.day <= 10) or
            (current_month % 12 == input_date.month and input_date.day >= 11) or
            ((current_month + 1) % 12 == input_date.month and input_date.day <= 10)
        ):
            return f'M{i} - {input_date.year}'
        current_month += 1
    return None

def get_role_name(project_id, userid):
    try:
        user = redmine.user.get(userid)
        data = user.memberships.__dict__

        for resource in data['_resources']:
            if str(resource['project']['id']) == str(project_id):
                roles = resource['roles']
                role_names = [role['name'] for role in roles]

                if any("client" in role.lower() for role in role_names):
                    return 'Client'
                else:
                    return 'CA'
    except redminelib.exceptions.ResourceNotFoundError:
        # Handle the exception to indicate that the user does not exist
        return 'User does not exist'

    return '' 


json_array = []
for issue in issues:

    data = issue._decoded_attrs
  

    issueid = data['id']
    priority = issue.priority
    tracker = issue.tracker
    subject = data['subject']
    description = data['description']
    created_on1 = data['created_on']
    created_on = datetime.strptime(created_on1, "%Y-%m-%dT%H:%M:%SZ") 
    if 'assigned_to' in data:
        assigned_to = data['assigned_to']['name']
    else:
        assigned_to = ''
    author = data['author']['name']
    author_id = data['author']['id']
    priority = data['priority']['name']
    status = data['status']['name']
    tracker = data['tracker']['name']
    project = data['project']['name']
    journaldata = issue['journals']

    tatc = 0
    tatu = 0
    
    first_json_obj = {"issue":issueid,"priority":priority,"tracker":tracker,"created_on": created_on,"created_by":author,"updated_by":"","updated_on":created_on,"old_status":"","new_status":"New","old_assignee":"","new_assignee":assigned_to,"notes": description,"old_assigneeid":"","new_assigneeid":"","tatc":tatc,"tatu":tatu}            
    
    json_array.append(first_json_obj)
    tempupdate = created_on      
    
    aa1 = sorted(journaldata['_resources'], key=lambda x: (x["created_on"]))
    for iteration in aa1:
            
        notes = iteration['notes']
        username = iteration['user']['name']

        updated_on = iteration['created_on']


        old_value =''
        new_value = ''
        old_assignee = ''
        new_assignee = ''
        old_assigneeid = ''
        new_assigneeid = '' 


        for details in iteration['details']:
            if details['name'] == 'status_id':
                try:
                    if type(details['old_value']) == str:
                        old_value = statuses(int(details['old_value']))
                    if type(details['new_value']) == str:
                        new_value = statuses(int(details['new_value']))
                except (redminelib.exceptions.ResourceNotFoundError, redminelib.exceptions.ResourceSetIndexError):
                        new_value = ''
                        old_value =''


            
            if details['name'] == 'assigned_to_id':
                
                if type(details['old_value']) == str:
                    try:
                        issue_old_username = redmine.user.get(int(details['old_value']))
                        old_assignee = str(issue_old_username)
                        old_assigneeid = details['old_value']
                    except redminelib.exceptions.ResourceNotFoundError:
                        print('User does not exist')
                        old_assignee = ''

                if type(details['new_value']) == str:
                    try:
                        issue_new_username = redmine.user.get(int(details['new_value']))
                        new_assignee = str(issue_new_username)
                        new_assigneeid = details['new_value']
                    except (redminelib.exceptions.ResourceNotFoundError, redminelib.exceptions.ResourceNotFoundError):
                        print('User does not exist')
                        new_assignee = ''
                
        

        if isinstance(created_on, str):
            created_datetime = created_datetime
        else:
            created_datetime = created_on

        if isinstance(updated_on, str):
            update_datetime = datetime.strptime(updated_on,  "%Y-%m-%d %H:%M:%S")
        else:
            update_datetime = updated_on
        time_difference1 = created_datetime - update_datetime
        time_difference2 = update_datetime - tempupdate
        tempupdate = update_datetime
        

        # Get the difference in hours as a floating-point number
        TATC = abs(time_difference1.total_seconds() / 3600)
        TATU = abs(time_difference2.total_seconds() / 3600)
    
        json_object = {"issue":issueid,"priority":priority,"tracker":tracker,"created_on": created_on,"created_by":author,"updated_by":username,"updated_on":updated_on,"old_status":old_value,"new_status":new_value,"old_assignee":old_assignee,"new_assignee":new_assignee,"notes": notes,"old_assigneeid":old_assigneeid,"new_assigneeid":new_assigneeid,"tatc":TATC,"tatu":TATU}            
        
        json_array.append(json_object)
            

temp_bucket = "CA"
oldissue = 0
for i in range(len(json_array)):
    if oldissue != json_array[i]['issue'] :
        json_array[i]['bucket'] = temp_bucket
    if i == 0:
        json_array[i]['bucket'] = temp_bucket
        if json_array[i]['new_assigneeid'] != '':
            temp_bucket = get_role_name(project_id,json_array[i]['new_assigneeid'])
            json_array[i]['bucket'] = temp_bucket
            oldissue = json_array[i]['issue']
        oldissue = json_array[i]['issue']
        continue
    if json_array[i]['old_assignee'] != "":
        temp_bucket = get_role_name(project_id,json_array[i]["old_assigneeid"])
    json_array[i]['bucket'] = temp_bucket
    if json_array[i]['old_assignee'] != "":    
        temp_bucket = get_role_name(project_id,json_array[i]['new_assigneeid'])
    oldissue = json_array[i]['issue']


filtered_json_array = json_array

for entry in filtered_json_array:
    
    # Calculate Month
    entry['month'] = result = get_month(entry['created_on'], 11, 4)
    # Calculate Severity
    if entry['priority'] == 'Showstopper':
        severity_value = severnity['Showstopper']
    elif entry['priority'] == 'High':
        severity_value = severnity['High']
    elif entry['priority'] == 'Medium':
        severity_value = severnity['Medium']  
    else:
        severity_value = severnity['Low']

    entry['severity'] = severity_value

tatu_sum_by_issue = {}  # Dictionary to store the total 'tatu' sum for each issue

current_issue = None
current_sum = 0
oldissue = ''
oldsum = 0

for entry in filtered_json_array:
    issue = entry['issue']
    bucket = entry['bucket']
    tatu = entry['tatu']
    status = entry['new_status']

    if issue != oldissue:
        if (oldissue, 'CA') not in tatu_sum_by_issue:
            tatu_sum_by_issue[(oldissue, 'CA')] = oldsum
    print(oldissue)
    
    # Check if it's a new issue
    if issue != current_issue:
        current_issue = issue
        current_sum = 0  # Reset the sum for the new issue
        newcurrentsum = 0
    # Add the 'tatu' value to the sum for the issue if the bucket is 'CA' and the status is not 'Client'
    if bucket == 'CA' and status != 'Client':
        current_sum += tatu
        oldsum = current_sum
          # If the current status is 'Delivered', store the sum for the issue
        if status == 'Delivered':
            tatu_sum_by_issue[(issue,bucket)] = current_sum
          
    if bucket != 'CA':
        newcurrentsum += tatu
        tatu_sum_by_issue[(issue,bucket)] = newcurrentsum
        if status == 'Delivered':
            tatu_sum_by_issue[(issue,bucket)] = newcurrentsum

    oldissue=issue

            
if (oldissue, 'CA') not in tatu_sum_by_issue:
        tatu_sum_by_issue[(oldissue, 'CA')] = oldsum

# Ensure that the sum is not negative
for issue, value in tatu_sum_by_issue.items():
    tatu_sum_by_issue[issue] = max(0, value)


# Iterate through the data again and add "CA_consume" and "Client_consume" keys based on the sum of tatu
for entry in filtered_json_array:
    issue = entry['issue']
    bucket = entry['bucket']
    severity = entry['severity']
    # Get the sum of tatu for the issue and bucket
    tatu_sum = tatu_sum_by_issue.get((issue, bucket), 0)
    
    
    if bucket == 'CA':
        entry['CA_consume'] = tatu_sum
        entry['Client_consume'] = 0
    elif bucket == 'Client':
        entry['CA_consume'] = 0
        entry['Client_consume'] = tatu_sum
    else:
        # Set default values when bucket is neither 'CA' nor 'Client'
        entry['CA_consume'] = 0
        entry['Client_consume'] = 0




# Create a dictionary to store the latest status for each issue group
latest_statuses = {}

# Iterate through the issues to determine the latest status for each group
for issue in filtered_json_array:
    issue_key = issue["issue"]
    new_status = issue["new_status"].lower()  # Convert "new_status" to lowercase

    if issue_key not in latest_statuses:
        latest_statuses[issue_key] = new_status
    elif new_status == "delivered":
        latest_statuses[issue_key] = "Delivered"

# Add a "finalstatus" column to each issue group
for issue in filtered_json_array:
    issue_key = issue["issue"]
    final_status = "Delivered" if latest_statuses[issue_key] == "Delivered" else "Open"
    issue["finalstatus"] = final_status



# NEW

# Dictionary to track the latest bucket for each issue group
issue_group_buckets = {}
issue_group_items = []
# Loop through the filtered_json_array
for item in filtered_json_array:
    issue = item["issue"]
    bucket = item["bucket"]
    new_assignee = item["new_assigneeid"] 

    # Check if new_assignee is not empty
   
    if new_assignee != "":   
        finalbucket = get_role_name(project_id, new_assignee)
        print(new_assignee)
        print("HP1111finalbucket",finalbucket)
    else:
        # Check if the issue group has been encountered before
        if issue in issue_group_buckets:
            finalbucket = issue_group_buckets[issue]
        else:
            # Find all items with the same issue and get the latest bucket
            issue_group_items = [i for i in filtered_json_array if i["issue"] == issue]
            finalbucket = max(issue_group_items, key=lambda x: x["updated_on"])["bucket"]
        
        # Update the issue group's finalbucket
        issue_group_buckets[issue] = finalbucket

    # Add the "finalbucket" field to all items in the issue group
    for group_item in issue_group_items:
        group_item["finalbucket"] = finalbucket


# Create a dictionary to store the latest update time for each issue group
latest_update_times = {}
# Calculate the current time
current_time = datetime.now()
# Iterate through the issues to determine the latest update time for each group
for issue in filtered_json_array:
    issue_key = issue["issue"]
    updated_on = issue["updated_on"]

    if issue_key not in latest_update_times:
        latest_update_times[issue_key] = updated_on
    elif updated_on > latest_update_times[issue_key]:
        latest_update_times[issue_key] = updated_on

# Update CA_consume for issues with 'finalstatus' as 'Open'
for issue in filtered_json_array:
    if issue["finalstatus"] == 'Open' :
        if issue["finalbucket"] == "CA":
            issue_key = issue["issue"]
            time_diff = (current_time - latest_update_times[issue_key]).total_seconds() / 3600
            if  issue["CA_consume"] != 0 :
                issue["CA_consume"] += time_diff
        else :
            issue_key = issue["issue"]
            time_diff = (current_time - latest_update_times[issue_key]).total_seconds() / 3600
            if  issue["Client_consume"] != 0 :
                issue["Client_consume"] += time_diff


# Define the keys to exclude
exclude_keys = ["old_assigneeid", "new_assigneeid"]

# Create a new dictionary without the excluded keys
filtered_json_array = [
    {key: value for key, value in item.items() if key not in exclude_keys}
    for item in json_array
]


severity_thresholds = {1: 1.5, 2: 2.5, 3: 2*24 + 4, 4: 4*24 + 8}

for entry in filtered_json_array:
    threshold = severity_thresholds.get(entry['priority'], 0)
    entry['breachstatus'] = 'Breached' if entry['CA_consume'] > threshold else ''

# Set the same breachstatus for all rows of the same issue
for issue in set(entry['issue'] for entry in filtered_json_array):
    breach_status = next((entry['breachstatus'] for entry in filtered_json_array if entry['issue'] == issue and entry['breachstatus']), '')
    for entry in filtered_json_array:
        if entry['issue'] == issue:
            entry['breachstatus'] = breach_status

issue_statuses = {}

for entry in filtered_json_array:
    issue = entry['issue']
    breachstatus = entry['breachstatus']
    
    if issue not in issue_statuses:
        issue_statuses[issue] = 'Breached' if breachstatus == 'Breached' else 'Not Breached'
    elif issue_statuses[issue] == 'Not Breached' and breachstatus == 'Breached':
        issue_statuses[issue] = 'Breached'

for entry in filtered_json_array:
    issue = entry['issue']
    entry['breachstatus'] = issue_statuses[issue]



# Write the json_array to a CSV file
csv_filename = str(project) + "-" +csv_output_name['detailed_csv']
full_filepath = csv_path + csv_filename
print('full_filepath-->',full_filepath)

# Check if the file exists and remove it if it does
if os.path.exists(csv_filename):
    os.remove(csv_filename)

# Create a list of fieldnames you want to include in the CSV
fieldnames = ["issue", "month", "severity", "priority", "tracker", "old_status", "new_status", "old_assignee", "new_assignee", "notes", "bucket", "created_on", "created_by", "updated_by", "updated_on", "tatu", "tatc", "CA_consume", "Client_consume", "breachstatus","finalstatus","finalbucket"]

# Open the CSV file for writing
with open(full_filepath, mode='w', newline='', encoding='utf-8') as csv_file:
   
    
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()  # Write the header row
    
    for data_entry in filtered_json_array:
        writer.writerow(data_entry)
    print(f"CSV file '{csv_filename}' has been created and saved to {full_filepath}")


# Create a Pandas DataFrame from the data
df = pd.DataFrame(filtered_json_array)

# Add 'month' and 'severity' columns based on logic
df['severity'] = df['priority'].apply(lambda x: '1 & 2' if x in ('High', 'Showstopper') else '3 & 4')

# Group by 'month' and 'severity' and calculate counts
summary_df = df.groupby(['month', 'severity'])[['issue']].nunique().reset_index()
summary_df = summary_df.rename(columns={'issue': 'Total'})


# Group by 'month', 'severity', and count distinct 'issue' values where 'breachstatus' is 'Breached'
SLApastcount_df = df[df['breachstatus'] == 'Breached'].groupby(['month', 'severity'])[['issue']].nunique().reset_index()
SLApastcount_df = SLApastcount_df.rename(columns={'issue': 'SLAFailedCount'})

# Merge the 'SLApastcount' column into the summary DataFrame
summary_df = summary_df.merge(SLApastcount_df, on=['month', 'severity'], how='left')

# Fill NaN values with 0
summary_df = summary_df.fillna(0)

# Convert the summary DataFrame to JSON
summary_json = summary_df.to_dict(orient='records')

for entry in summary_json : 
    entry["SLAmeet"] = ((entry["Total"] - entry["SLAFailedCount"]) / entry["Total"] ) * 100

    if entry["severity"] == "1 & 2":
        entry["Goal"] = goal['one_and_two']
        if entry["SLAmeet"] > entry["Goal"] : 
            entry["GoalMet"] = 'Y'
        else : 
            entry["GoalMet"] = 'N'
    else :
        entry["Goal"] = goal['three_and_four']
        if entry["SLAmeet"] > entry["Goal"] : 
            entry["GoalMet"] = 'Y'
        else : 
            entry["GoalMet"] = 'N'


# Write the json_array to a CSV file
csv_filename = str(project) + "-" +csv_output_name['monthwise_csv']
full_filepath = csv_path + csv_filename
print('full_filepathsummry-->',full_filepath)


fieldnames = ["month","severity","Total","SLAFailedCount","SLAmeet","Goal","GoalMet" ]     
with open(full_filepath, mode='w', newline='', encoding='utf-8') as csv_file:
                    
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()  # Write the header row
        
        for data_entry in summary_json:
            # Exclude 'index' and 'time' fields from the data_entry dictionary
            data_entry = {key: value for key, value in data_entry.items() if key in fieldnames}
            writer.writerow(data_entry) 
        print(f"CSV file '{csv_filename}' has been created and saved to {full_filepath}")


# Calculate the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time    

# Calculate minutes and seconds
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
# Print the elapsed time in minutes and seconds
print(f"Time taken for code execution: {minutes} minutes {seconds} seconds")  
print('Execution Ended')

