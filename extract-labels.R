# For cross-validation, retrieve labels
# orig: jtlindgren 13mar2015

# Clean memory
#rm(list=ls())

# GDF files are read from here. In this version, only expect concatenated file of one participant
signalFile<-"./signals/concatenated_training.gdf";

# the label are written here
outputFilename<-"./signals/concatenated_training.csv"

g_NoGui<- "--no-gui"; # set to empty "" to see the GUI, good for debugging

# adapt binary location to system
switch (Sys.info()[['sysname']],
    Windows= {
        g_Designer<-"C:/Program Files/openvibe-2.2.0-64bit/openvibe-designer.cmd"
    },
    Linux  = {
        g_Designer<-"ov-designer-2.2";
    },
    Darwin = {
        g_Designer<-"ov-designer-2.2";
    }
)

g_Scenario<-"extract-labels.xml"

#### should be nothing to modify below this

if (file.exists(outputFilename)) {
    stop(sprintf("Output file [%s] already exists, abort to prevent overwite.\n", outputFilename))
}

cat("Processing dataset...\n")

cmd<-sprintf("\"%s\" -d User_InputDataset %s -d User_OutputLabels %s --no-session-management %s --play-fast %s",
        g_Designer, signalFile, outputFilename, g_NoGui, g_Scenario);
cat(cmd,"\n"); flush.console();
system(cmd);
flush.console();

cat("\n")


cat("Done.\n");

