# Concatenate GDF files recording during training (2 per subject)

# Clean memory
rm(list=ls())

# GDF files are read from here, there will be one folder per participants (format subjec_xxx), calibration filename format motor-imagery-csp-1-acquisition-[2016.08.04-15.55.00].gdf
datasetFolder<-"../signals/";
# file format recorded during calibration
datasetPattern<-"motor-imagery-csp-1-acquisition-.*\\.gdf";

# the label and signal CSV files are written here, will be created if does not exist
outputFolder<-"dataset-orig";


g_NoGui<- "--no-gui"; # set to empty "" to see the GUI, good for debugging
g_Designer<-"ov-designer-2.2";
g_Scenario<-"concatenate.xml" 

#### should be nothing to modify below this

# if output folder does not exist, make it
dir.create(outputFolder, showWarnings=FALSE)

# gathering subjects, which should have sub-folders in input directory
listSubjects <- list.files(datasetFolder,pattern="subject_*",recursive=FALSE);
cat("List of subjects:", listSubjects, "\n")

# checking if corresponding output exists, format subject_xxx.gdf
outputFiles<-list.files(outputFolder,pattern="subject_.*_training\\.gdf",recursive=FALSE);
cat("Existing output:", outputFiles, "\n")

# will only take into account new ones
newSubjects <- c()
for (sub in listSubjects) {

    if (is.na(match(sprintf("%s_training.gdf", sub), outputFiles) ))
    {
        newSubjects <- c(newSubjects, sub)
    }
}
cat("Will process new subjects:", newSubjects, "\n\n")

for(nsub in newSubjects)
{
    cat("Processing subject:", nsub, "\n")
    
    # retriving list of files, check that we only get two
    signalFiles <- list.files(paste(datasetFolder, nsub, sep=""),pattern=datasetPattern,recursive=FALSE);
    cat("Found files:", paste(datasetFolder, nsub, "/", signalFiles, sep=""))
    
    if (length(signalFiles) != 2) {
        warning("Invalid data, only supports contatenation of 2 sessions, skipping subject.\n\n")
        next
    }
    
    # build path for openvibe
    signalFile1 <-sprintf("%s%s/%s", datasetFolder, nsub, signalFiles[1]);
    signalFile2 <-sprintf("%s%s/%s", datasetFolder, nsub, signalFiles[2]);
    
    outputSignal<-sprintf("%s/%s_training.gdf", outputFolder, nsub);	

    cat("Processing dataset...\n")

    cmd<-sprintf("\"%s\" -d User_InputDataset_1 %s -d User_InputDataset_2 %s -d User_OutputSignal %s --no-session-management %s --play-fast %s",
            g_Designer, signalFile1, signalFile2, outputSignal, g_NoGui, g_Scenario);
    cat(cmd,"\n"); flush.console();
    system(cmd);
    flush.console();

    cat("\n")
}

cat("Done.\n");

