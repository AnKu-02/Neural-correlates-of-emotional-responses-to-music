'''
This script deals with the preprocessing of the data. It reads the raw data from the BIDS dataset,
and applies the following preprocessing steps:

1. Reads the raw data from the BIDS dataset
2. Reads the annotations from the BIDS dataset
3. Sets the EEG reference to average
4. Sets the montage to standard_1020
5. Filters the data between 1Hz and 100Hz
6. Downsamples the data to 200Hz
7. Breaks the data into 1s epochs
8. Applies autoreject to the epochs
9. Fit ICA to the epochs
10. Applies ICALabel to the ICA components
11. Removes the ICA components that are not brain or other
12. Applies the ICA to the raw data
13. Filters the data between 1Hz and 40Hz to remove line noise
14. Saves the data as EDF
'''


import json
import mne
import sys

import pandas
sys.path.insert(0, '.')
import ccs_eeg_utils

import matplotlib.pyplot as plt

from mne import events_from_annotations
from mne_bids import BIDSPath, read_raw_bids, write_raw_bids

from autoreject import AutoReject
from mne_icalabel import label_components

import time

# path where to save the datasets.
bids_root = "/home/fsociety/Documents/Datasets/project-dataset"
output_root = "/home/fsociety/Documents/Datasets/project-output"

start_sub = 1
end_sub = 31
subjects = [f"{i:02d}" for i in range(start_sub, end_sub+1)]

runs = ['run1', 'run2', 'run3', 'run4', 'run5', 'run6']

start_time = time.time()
print("Starting the preprocessing pipeline!!!")
for subject in subjects:
    for run in runs:
        try:
            print()
            print("-----------------------------------")
            print("Processing subject: ", subject, " run: ", run)
            print("-----------------------------------")
            
            bids_path = BIDSPath(subject=subject,task=run,
                        datatype='eeg', suffix='eeg',
                        root=bids_root)
            
            # read the file
            raw = read_raw_bids(bids_path, verbose=False)
            # fix the annotations readin
            ccs_eeg_utils.read_annotations_core(bids_path,raw)
            raw.load_data(verbose=False)
            raw.set_eeg_reference("average", verbose=False)
            raw.set_montage('standard_1020',match_case=False)

            hi_cut  = 100 # ICALabel needs a bandpass of 1Hz to 100Hz
            low_cut = 1 # ICA requires a high pass of 1Hz

            # filtered copy of raw data
            raw_f = raw.copy().filter(low_cut, hi_cut, fir_design='firwin', verbose=False)
                        
            raw_f.set_montage('standard_1020',match_case=False)
            raw_f.set_eeg_reference("average", verbose=False)
            
            # Downsample the data to 200Hz (2xhi_cut) for speed purposes
            raw_downsampled = raw_f.resample(2*hi_cut)
            
            # Break raw data into 1 s epochs
            tstep = 1.0
            events_ica = mne.make_fixed_length_events(raw_downsampled, duration=tstep)
            epochs_ica = mne.Epochs(raw_downsampled, events_ica,
                                    tmin=0.0, tmax=tstep,
                                    baseline=None,
                                    preload=True, verbose=False)
            
            # Apply autoreject remove bad epochs
            ar = AutoReject(n_interpolate=[1, 2, 4],
                    random_state=42,
                    picks=mne.pick_types(epochs_ica.info, 
                                        eeg=True,
                                        eog=False
                                        ),
                    n_jobs=-1, 
                    verbose=False
                    )

            ar.fit(epochs_ica)
            reject_log = ar.get_reject_log(epochs_ica)
            
            # ICA parameters    
            random_state = 42          # ensures ICA is reproducible each time it's run
            ica_n_components = .99     # Specify n_components as a decimal to set % explained variance

            # Fit ICA
            ica = mne.preprocessing.ICA(n_components=ica_n_components,
                                        random_state=random_state,
                                        method = 'infomax',         # recommended by ICALabel (extended infomax)
                                        fit_params=dict(extended=True),
                                        verbose=False)
            
            ica.fit(epochs_ica[~reject_log.bad_epochs], decim=3, verbose=False)
            ic_labels = label_components(raw_downsampled, ica, method="iclabel")
            labels = ic_labels["labels"]

            # Remove components that are not brain or other
            exclude_idx = [idx for idx, label in enumerate(labels) if label not in ["brain", "other"]]
            ica.exclude = exclude_idx
            ica_filtered = raw_downsampled.copy()
            
            # reconstruct filtered data with ICA
            ica.apply(ica_filtered, exclude=exclude_idx, verbose=False)
            ica_filtered.filter(1, 40, fir_design='firwin', verbose=False)
            
            # save overlay plot for visual inspection            
            fig = ica.plot_overlay(raw_downsampled, show=False, exclude=exclude_idx)
            fig.savefig(output_root + "/figures/" + subject + "_" + run + "_overlay.png")
            plt.close(fig)
            
            # generate output bids path to save the data
            output_bids_path = BIDSPath(subject=subject,task=run,
                        datatype='eeg', suffix='eeg',
                        root=output_root)
            
            
            # READ EVENT ID AND EVENTS
            event_id = {}
            with open("/home/fsociety/Documents/Uni-Stuttgart/WS2023_24/brain_potentials/Assignments/event_ids.json") as f:
                event_id = json.load(f)

            # read a tsv file, generate events numpy array
            df = pandas.read_csv(bids_root+"/sub-"+subject+"/eeg/sub-"+subject+"_task-"+run+"_events.tsv",sep='\t')
            events = df[['sample','duration', 'value']].values.astype(int)

            # set annotations to None, so they dont get mixed up with our custom events
            ica_filtered.set_annotations(None)
            write_raw_bids(ica_filtered, output_bids_path, overwrite=True, 
                        allow_preload=True, format='EDF',
                        event_id=event_id, events=events, verbose=False
            )
            
            # save psd plot for visual inspection
            fig = ica_filtered.compute_psd().plot()
            fig.savefig(output_root + "/figures/" + subject + "_" + run + "_psd.png")
            plt.close(fig)
            
            
            # delete all variables to free up memory
            del raw
            del raw_f
            del raw_downsampled
            del epochs_ica
            del ica_filtered
            del ica
            del ar
            del reject_log
            
        except Exception as e:
            print("Error in subject: ", subject, " run: ", run, e)
            # sys.exit(1)

print("Preprocessing pipeline completed!!!")
print("--- %s minutes ---" % ((time.time() - start_time)//60))  
print("--- %ss per run ---" % ((time.time() - start_time)//(len(subjects)*len(runs))))
print("--- %ss per subject ---" % ((time.time() - start_time)/(len(subjects))))
print("--- %s total runs ---" % (len(subjects)*len(runs)))