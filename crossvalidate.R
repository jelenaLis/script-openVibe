# Runs openvibe on a previously generated crossvalidation folding
# jtlindgren feb2015

# Clean memory
rm(list=ls())

g_NoGui<-"--no-gui"; # set to empty ""  to see the GUI, good for debugging
g_Designer<-"ov-designer-2.2";

#g_NoGui<-"";

g_TrainScenarios<-c("cross_valid/mi-csp-2-train-CSP.xml", "cross_valid/mi-csp-3-classifier-trainer.xml"); # can be any number of them, run in order of listing
g_TestScenario<-"cross_valid/mi-csp-5-replay.xml";

#### should be nothing to modify below this

# load the folding
fn<-sprintf("cross_valid/fold_info.RData");
load(file=fn);
		
# crossvalidate
for(dsetIdx in 1:length(folds))
{	
	for(foldIdx in 1:length(folds[[dsetIdx]]$trainFiles))
	{
		trainFile<-folds[[dsetIdx]]$trainFiles[foldIdx];
		testFile<-folds[[dsetIdx]]$testFiles[foldIdx];
		signalFile<-folds[[dsetIdx]]$signalFile;
		modelFile<-folds[[dsetIdx]]$modelFiles[foldIdx];
		predictionFile<-folds[[dsetIdx]]$predictionFiles[foldIdx];
		
		cat("Dataset# ", dsetIdx, ", signal [", signalFile, "] train [", trainFile, "] test [", testFile, "] output model [", modelFile, "]\n");

		cat("Training fold ", foldIdx, " ...\n");
		for(scenario in g_TrainScenarios)
		{
			cmd<-sprintf("\"%s\" -d User_Signal %s -d User_TrainFold %s -d User_Model %s --no-session-management %s --play-fast %s",
				g_Designer, signalFile, trainFile, modelFile, g_NoGui, scenario);
			cat(cmd,"\n"); flush.console();
			system(cmd);
			flush.console();
		}
		
		cat("Testing fold ", foldIdx, " ...\n");
		cmd<-sprintf("\"%s\" -d User_Signal %s -d User_TestFold %s -d User_Model %s -d User_Prediction %s --no-session-management %s --play-fast %s",
			g_Designer, signalFile, testFile, modelFile, predictionFile, g_NoGui, g_TestScenario);
		cat(cmd,"\n"); flush.console();
		system(cmd);
		flush.console();
	}
}

cat("Finished crossvalidating.\n");

