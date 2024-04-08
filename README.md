# Neural-correlates-of-emotional-responses-to-music

This project is part of course Signal processing and Analysis of human brain potentials (EEG) at University of Stuttgart.

## Overview
This project proposes an enhanced framework for preprocessing and analyzing EEG (Electroencephalography) data, specifically focusing on the neural correlates of emotions induced by music. Building on the pioneering work of Ian Daly et al., our framework integrates mne-ICLabel for artifact detection, FastICA for component analysis, and an automated rejection algorithm for epoch selection. We aim to simplify the preprocessing step by eliminating the need for a 50Hz notch filter and ensuring more efficient data processing while preserving data integrity.

## Team Members
- Souvik Saha
- Ananya Kulkarni

## Key Features
- **Automated Artifact Detection**: Utilization of mne-ICLabel for identifying and eliminating artifacts more efficiently.
- **Component Analysis**: Implementation of FastICA within mne-python to break down the EEG signal into its components.
- **Epoch Selection**: Application of an automated rejection algorithm for selecting high-quality epochs.
- **Simplified Filtering Process**: Proposing a bandpass filtering method that eliminates the need for a 50Hz notch filter, making the preprocessing step simpler and more straightforward.

## Methodology
1. **Data Import**: Import raw EEG data structured with the BIDS standard.
2. **Preprocessing**: Includes bandpass filtering, downsampling, epoching, artifact detection, and removal.
3. **Component Analysis**: Utilizes Independent Component Analysis (ICA) to identify and remove components associated with artifacts.
4. **Signal Reconstruction**: Applies the inverse of the ICA, using only the components believed to be brain-related, to recreate the cleaned EEG signal.

## Challenges Encountered
- **Data Accessibility**: The original link for the dataset was inactive, complicating access to music data correlated with EEG recordings.
- **Incomplete Annotations**: A significant portion of the EEG runs lacked precise annotations, limiting the depth of analysis possible.
- **Dataset Discrepancies**: Uncertainties regarding the specific sets of music used during EEG sessions and inconsistencies within the dataset documentation.

## Conclusions and Future Work
Our project highlights the potential of modern computational tools in improving EEG data analysis, particularly in studying emotional responses to music. While the proposed modifications offer a more streamlined and efficient preprocessing pathway, challenges such as dataset accessibility and annotation completeness limit the scope of our analysis. Future studies should focus on resolving these issues, ensuring comprehensive music annotations, and expanding the dataset to allow for more conclusive research into the neural basis of music-induced emotions.

## References
Ian Daly et al., "Neural correlates of emotional responses to music: An EEG study," Neuroscience Letters, 2014.
- Link to the paper: https://doi.org/10.1016/j.neulet.2014.05.003

## Dataset Link
An EEG dataset recorded during affective music listening - https://openneuro.org/datasets/ds002721/versions/1.0.2.
