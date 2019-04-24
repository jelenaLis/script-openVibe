Running the tuxflow experiment, (sometimes) biasing the classifier output to boost flow with a Tux racer game.

# How-to Tux2

Using Brain Products Liveamp, 32 electrodes.

Tested with OpenViBE 2.2.0 with Python 2.7 (windows & linux), R 3.4.4 through RKward (windows & linux).

Launch OpenViBE server, select liveamp driver, 32 electrodes, 500 Hz, with accelerometer. Set drift to 10ms. Use chunk size 4.

## Setup

Run`mi-csp-0-signal-monitoring.xml` -- also possible check impedance through OpenViBE server.

## Calibration 

Acquisition: launch tux, launch scenario `mi-csp-1-acquisition.xml` until end circuit. Two times.

Concatenation: run `concatenate.R`

Select frequency: scenario `mi-csp-1bis-frequencyBandSelection.xml`

Train spatial filter: `mi-csp-2-train-CSP.xml`

Train classifier: `mi-csp-3-classifier-trainer.xml`

## Experiment

During XP: launch LSL2Joy

Between each run: generate new circuit.

For each run, launch Tux, launch `mi-csp-4-online_noadapt.xml`, start track special BCI.

## Bonus

Participant can try regular track through scenario `mi-csp-4bis-online_noadapt_truetrue.xml`.

# Files description

## OpenViBE files

Taken from classical motor imagery scenarios, also contribution from Jussi Lindgren and Fabien Lotte.

* mi-csp-0-signal-monitoring: look at signals
* mi-csp-1-acquisition: record graz session
* mi-csp-1bis-frequencyBandSelection.xml: select band frequency
* mi-csp-2-train-CSP: train spatial filter
* mi-csp-3-classifier-trainer: train the (SVM) classifier

* mi-csp-4-online_noadapt: control tux / record data
* mi-csp-4-online_adapt: control tux / record data, this version bias the classifier with positive feedback

* replayer_adapt.xml: used in ./stats to retrieve online data

### pyhton files used within scenarios

* python_lsl_stims.py: python box to retrieve stimulation from tux through LSL
* ov_bias_adapt_classifier_vidaurre.py: center output between run, bias depending of conditions, enable / disable classifier output in order to limit tux movements

## Folders

* libs: required by the OpenViBE python box that fetch stimulation from tux racer.

NB: the file "liblsl.so" comes from a previous OpenViBE installation, for convenience. It may be needed to replace it with one coming from the computer running the expirement if OpenViBE crashes upon init (location: openvibe_folder/dependencies/lib).

* signals: empty on purpose, OpenViBE will write data in here, also conain most scenarios' output configuration to ease backup.

NB: two files will be recorded : one containing EEG data and the other the output of the classifier (*_EEG.gdf and *_class.gdf respectively). Both have the same stimulations (recorded from tux racer)

### From tux1

* analyses: OpenViBE scenarios aimed at analysing offline previously recorded data
* data: mp3 for the "music" condition
* scripts: bash scripts that will facilitate the experiment (e.g. switch between the music)
* stats: first try for R statistics. Questionnaires data retrieved from the online formulaires, converted to CSV. 