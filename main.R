
# Will take care of launching all scripts related to calibration data
# NB: first CD to current script directory

runOV <- function(scenarioFile) {
    # adapt OpenViBE binary location to system -- TODO: factorize between all scripts
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
    g_NoGui<- "--no-gui"; # set to empty "" to see the GUI, good for debugging

    cmd<-sprintf("\"%s\" --no-session-management %s --play-fast %s", g_Designer,  g_NoGui,  scenarioFile);
    cat(cmd,"\n");
    flush.console();
    system(cmd);
    flush.console(); 
}

# concatenation
source("concatenate.R")

# select frequency
runOV("mi-csp-1bis-frequencyBandSelection.xml")

# machine learning for testing
runOV("mi-csp-2-train-CSP.xml")
runOV("mi-csp-3-classifier-trainer.xml")

# data for cross-validation
#source("extract-labels.R")
#source("generate-folding.R")
#source("crossvalidate.R")
#source("aggregate.R")


