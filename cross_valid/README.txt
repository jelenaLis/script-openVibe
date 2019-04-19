

Scripts adapted from Jussi's examples.

Bump to OpenViBE 2.2.

NB: CSV Writer/Reader still use deprecated box because the new one at the moment necessitate a (useless here) signal stream, and do not let customize separators.

Beware: change epoch offset and duration in mi scripts (stimulation based epoching + lua script switch director) in order to match length on the trials with tux.

===


Trial-based cross-validation in OpenViBE, scripts ver v0.4c (scenarios updated for OpenViBE 1.3.0 at 14mar2017)

The most recent document version should be at

http://openvibe.inria.fr/tutorial-how-to-cross-validate-better

Instructions
-------------

This bunch of scripts shows how to do 'more proper' cross validation of OpenViBE 
motor imagery. With slight modifications, it can in principle be customized for
other scenarios. Using this is not very convenient, but it should work as a 
baseline when you need to get publication-quality crossvalidation results.


Some problems with openvibe cross-validation in 'classifier trainer' box
------------------------------------------------------------------------
The classifier trainer box works correctly in the machine learning sense:
you give it IID (independent and identically distributed) feature vectors,
and you get a correct crossvalidation result. However, this box cannot
be responsible what happens outside it. In practice, OpenViBE scenarios
create data in a manner that the IID assumption can be noticeably 
violated.

1) The cross-validation box cannot take into account the possibly
preceding CSP training stage; CSP can make an overfitting transform
for the data and the labels, before the classifier training stage 
takes place. The same is likely true for XDAWN filter. The final evaluating 
classifier is in this case e.g.  lda(filter(data)) == f(g(data)), but 
cross-validation only controlled the f() part, with data that g() had 
already overfitted.

2) Feature vectors from the same trial can end up both in testing and
train folds. Since the in-trial vectors may have large correlations 
between each other (time-correlating EEG), this is making the 
crossvalidation estimate from the classifier trainer box more optimistic. 

3) Test scenario is not used in the xval estimate given by the
'classifier trainer' box, leaving room for possible errors/discrepancies 
in the testing scenario or the 'classifier processor' box which will in
practice do the actual prediction.

Solution: do cross validation across trials by defining which time
segments of the signal belong to test and train folds globally, and 
use this same segmentation for training all the supervised learning
components in the DSP chain. Finally, make the predictions with an 
actual test scenario and then aggregate the predictions against 
known ground truth.


Operating principle of these scripts
------------------------------------

For each experiment,

  Take the stream of the timeline of an experiment (label stream).

  For each crossvalidation fold: 
  
    Assign the trials (time segments) to belong either to a test or a train fold

  Repeat over all the folds
  
    Filter the timeline in two different ways, generating two disjoint
    timeline files. In the TRAINING timeline file, trials assigned to training
    fold are kept as they are, whereas the test trials are filtered (stimulation 
	label set to 0). In the TESTING timeline file, the opposite is done.

    Now, run the training scenarios on the TRAINING timeline file ONLY, 
	and the test scenario on the TESTING timeline file ONLY (the signal file 
	will be the same for both).

    Save the result for each trial (i.e. time, real class, majority voted class for segment/trial)

Summarize all the results


In practice
-----------
The scripts present wrapper code to do whats described above. At the moment they 
are in R, but they could be made e.g. with Python. 

Requirements: R (at least 2.5.12 and later), compiled openvibe git "integration-1.0 branch(!)" 20.02.2015 or later

- Edit all the R files mentioned below and check that all the paths are correct

- Extract the labels from an OV file to a CSV file, get a pair: 01-signal.ov, 01-labels.csv. We
need the labels in CSV to be able to filter them in R. Put these files to whatever the datasetFolder 
variable is pointing to.  If you have several files, the next should be named 02-signal.ov, 02-label.csv, 
etc. For .ov files, this extraction can be done by connecting Generic Stream Reader to the
format corresponding output boxes, each writing the corresponding file. You'll need to do this only once. 

There's a convenience script for this

# source('extract-labels.R')

- Generate foldings (writes all filtered test/train label streams) by running in R

# source('generate-folding.R') 

- Run the training/testing on all these folds, by running in R

# source('crossvalidate.R')

- Finally, to collect & display the results

# source('aggregate.R')

Note that this script currently uses modified motor imagery scenarios: all the data/model paths in the
scenarios have been replaced with configuration tokens, so that crossvalidate.R can specify the files
to be used each time. If you want to run these scripts for other scenarios, you need to modify them
accordingly (study the MI scenarios).


 -- jtlindgren, 05mar2015
 
 
