# script-openVibe

Running the tuxflow experiment, (sometimes) biasing the classifier output to boost flow with a Tux racer game.

Tested with OpenViBE 1.2.1

## OpenViBE files

Taken from classical motor imagery scenarios. 

The "_fix" versions were used when electrodes were faltering. The "_tux" version is an attempt at using data from tux racer instead of graz for training.

* mi-csp-0-signal-monitoring: look at signals
* mi-csp-1-acquisition: record graz session
* mi-csp-2-train-CSP: train spatial filter
* mi-csp-3-classifier-trainer: train the (SVM) classifier

* mi-csp-4-online: not used, graz for real
* mi-csp-4-replay_adapt and mi-csp-4-replay_noadapt: for debugging, use recorded data instead of live signals to control tux

* mi-csp-4-online_noadapt: control tux / record data
* mi-csp-4-online_adapt: control tux / record data, this version bias the classifier with positive feedback

* replayer_adapt.xml: used in ./stats to retrieve online data

### pyhton files used within scenarios

* python_lsl_stims.py: python box to retrieve stimulation from tux through LSL
* ov_bias_classifier: enable / disable classifier output in order to limit tux movements
* ov_bias_adapt_classifier: the same, with a positive feedback bias
* visualFB_OV.py: ? most probably safe to delete

## Folders

* analyses: OpenViBE scenarios aimed at analysing offline previously recorded data

* data: mp3 for the "music" condition

* libs: required by the OpenViBE python box that fetch stimulation from tux racer.

NB: the file "liblsl.so" comes from a previous OpenViBE installation, for convenience. It may be needed to replace it with one coming from the computer running the expirement if OpenViBE crashes upon init (location: openvibe_folder/dependencies/lib).

* scripts: bash scripts that will facilitate the experiment (e.g. switch between the music)

* signals: empty on purpose, OpenViBE will write data in here.

NB: two files will be recorded : one containing EEG data and the other the output of the classifier (*_EEG.gdf and *_class.gdf respectively). Both have the same stimulations (recorded from tux racer)

* stats: first try for R statistics. Questionnaires data retrieved from the online formulaires, converted to CSV. 
