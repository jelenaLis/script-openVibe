####
#### See README.txt
#####
#### jtlindgren feb2015
####

# Clean memory
rm(list=ls())

# ov files are read from here
datasetFolder<-"dataset-orig";

# the label and signal CSV files are written here.
outputFolder<-"dataset-converted";

g_NoGui<-" " #--no-gui"; # set to empty "" to see the GUI, good for debugging
g_Designer<-"ov-designer-1.2";
g_Scenario<-"extract-labels.xml"

#### should be nothing to modify below this

signalFiles<-list.files(datasetFolder,pattern=".*ov$",recursive=TRUE);

dir.create(outputFolder, showWarnings=FALSE)

for(dsetIdx in 1:length(signalFiles))
#for(dsetIdx in 1:1)
{	
	signalFile<-sprintf("%s/%s", datasetFolder, signalFiles[dsetIdx]);
	
	escapedSignalFile<-gsub("/","-",signalFiles[dsetIdx]);	
	outputSignal<-sprintf("%s/%s_signal.ov", outputFolder, escapedSignalFile);	
	outputLabels<-sprintf("%s/%s_labels.csv", outputFolder, escapedSignalFile);
	
	cat("Processing dataset [", signalFile, "]...\n")
	
	cmd<-sprintf("\"%s\" --no-pause -d User_InputDataset %s -d User_OutputLabels %s -d User_OutputSignal %s --no-session-management %s --play-fast %s",
		g_Designer, signalFile, outputLabels, outputSignal, g_NoGui, g_Scenario);
	cat(cmd,"\n"); flush.console();
	system(cmd);
	flush.console();
	
	cat("\n")
}

cat("Done.\n");

