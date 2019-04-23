# Concatenate GDF files recording during training (2 per subject)

# Clean memory
rm(list=ls())

# GDF files are read from here. In this version, only expect one participant, whose files during calibration are named motor-imagery-csp-1-acquisition-[2016.08.04-15.55.00].gdf
datasetFolder<-"./signals/";
# file format recorded during calibration
datasetPattern<-"motor-imagery-csp-1-acquisition-.*_EEG\\.gdf";

# the label and signal CSV files are written here
outputFolder<-"./signals/";
outputFilename<-"concatenated_training.gdf"

g_NoGui<- "--no-gui"; # set to empty "" to see the GUI, good for debugging
g_Designer<-"ov-designer-2.2";
g_Scenario<-"concatenate.xml" 

#### should be nothing to modify below this

outputSignal <- paste(outputFolder, outputFilename, sep="")

if (file.exists(outputSignal)) {
    stop(sprintf("Output file [%s] already exists, abort to prevent overwite.\n", outputSignal))
}

# retriving list of files, check that we only get two
signalFiles <- list.files(datasetFolder, pattern=datasetPattern,recursive=FALSE);
cat("Found files:", paste(datasetFolder,  "/", signalFiles, sep=""))

if (length(signalFiles) != 2) {
    stop("Invalid data, only supports contatenation of 2 sessions.\n")
}

# build path for openvibe
signalFile1 <-sprintf("%s%s", datasetFolder, signalFiles[1]);
signalFile2 <-sprintf("%s%s", datasetFolder, signalFiles[2]);

cat("Processing dataset...\n")

cmd<-sprintf("\"%s\" -d User_InputDataset_1 %s -d User_InputDataset_2 %s -d User_OutputSignal %s --no-session-management %s --play-fast %s",
        g_Designer, signalFile1, signalFile2, outputSignal, g_NoGui, g_Scenario);
cat(cmd,"\n"); flush.console();
system(cmd);
flush.console();

cat("\n")

cat("Done.\n");

