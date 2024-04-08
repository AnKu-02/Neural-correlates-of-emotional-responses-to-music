'''
This file is the first step in the preprocessing pipeline. It reads the raw data from the BIDS dataset,
and adds a new column called value to the events.tsv file, which it gets from the events_keys.json file.
The missing values in the trial_type column are replaced with nan, and the rows with nan values are dropped.
'''

import json
import pandas
import zipfile
import shutil
from numpy import nan

# Read a TSV file into a DataFrame
fs = 200

start_sub = 1
end_sub = 31
subjects = [f"{i:02d}" for i in range(start_sub, end_sub+1)]

runs = ['run'+str(i) for i in range(1,7)]

root = "/home/fsociety/Documents/Datasets/project-dataset"

# delete old instance of root directory
shutil.rmtree(root)
print("Deleted root directory!!!")

with zipfile.ZipFile("/home/fsociety/Documents/Datasets/project-dataset.zip", 'r') as zip_ref:
    zip_ref.extractall("/home/fsociety/Documents/Datasets/")
print("Extracted zip file!!!")

# read json file with event keys
data = {}
with open("/home/fsociety/Documents/Uni-Stuttgart/WS2023_24/brain_potentials/Assignments/events_keys.json") as f:
    data = json.load(f)
    print(data)
    # change all keys to int
    data = {int(k):v for k,v in data.items()}
    
for subject in subjects:
    for run in runs:
        # read a tsv file
        try:
            df = pandas.read_csv(root+"/sub-"+subject+"/eeg/sub-"+subject+"_task-"+run+"_events.tsv",sep='\t')
            
            # copy values from trial_type to value
            df['value'] = df['trial_type']
            
            #replace values in column value with the values from the json file
            df['trial_type'].replace(to_replace=data, inplace=True)
            
            # if a value in trial type is not a string, make it nan
            df['trial_type'] = df['trial_type'].apply(lambda x: x if type(x)==str else nan)               
            
            # add a sample column and convert onset to samples by multiplying with sampling frequency
            df['sample'] = (df['onset']*fs).astype(int)
            
            # drop all rows with trial_type as 'na'
            df.dropna(subset=['trial_type'], inplace=True)
            print('Run: ', run, ' Subject: ', subject, ' pandalised successfully!!!')
            
            # save the dataframe as a tsv file
            df.to_csv(root+"/sub-"+subject+"/eeg/sub-"+subject+"_task-"+run+"_events.tsv",sep='\t',index=False)
        
        except FileNotFoundError:
            print("File not found for subject: ", subject, " run: ", run)
            continue

print("Pandaliser finished successfully!!!")