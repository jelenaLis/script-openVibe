# Generates cross-validating folding (filtered label stream timelines), two for each train+test fold pair.
# orig: jtlindgren 13mar2015

# Clean memory
#rm(list=ls())

# Number of folds
nFolds<-5;

# Make sure that each fold has the same amount of each class. requires input data to be balanced (i.e. exactly same number of trials for each class).
balanceLabels<-TRUE;

# assumes index correspondence between the two lists	
datasetFolder<-"signals"
labelFile<-"concatenated_training.csv";
signalFile<-"concatenated_training.gdf";

# filtered timelines (label streams) are written here
foldsFolder<-"cross_valid/folds";

# models are written here
modelsFolder<-"cross_valid/models";

# prediction voting are here
predictionsFolder<-"cross_valid/predictions";

# classifier output is here
classoutputFolder<-"cross_valid/class-output";

# numeric markers for OVTK_GDF_LEFT, OVTK_GDF_RIGHT. These are what will be filtered in the label stream.
classes<-c(769,770)


#### should be nothing to modify below this

# dirty hack, script was aimed at several files
labelFiles <- c(labelFile)
signalFiles <- c(signalFile)

folds<-list();

cnt<-1;
for(dsetIdx in 1:length(labelFiles))
#for(dsetIdx in 1:1)
{
	labelFile<-labelFiles[dsetIdx];
	fn<-sprintf('%s/%s', datasetFolder, labelFile);
	dat<-read.csv(fn, sep=";")

	cat("Processing dataset [", fn, "]...")
	
	# find stimulations corresponding to the numeric class markers we are interested in
	idxs<-which(dat[,2] %in% classes)
	if(length(idxs)==0) {
		cat("Error: Couldn't find any classes in the label file\n");
	}
	
	# permute these trials randomly
	idxs<-idxs[sample(1:length(idxs),replace=FALSE)]

	if(balanceLabels) {
		# re-sort the random-permuted idxs so that each class forms a continuous segment, e.g. [class1 class1 class1 class2 class2 ...]
		trialLabels<-dat[idxs,2];	
		for(j in 1:length(classes)) {
			if(j==1) {
				sortedIdxs<-idxs[which(trialLabels==classes[j])];
			} else {
				sortedIdxs<-c(sortedIdxs, idxs[which(trialLabels==classes[j])]);
			}
		}
		idxs<-sortedIdxs;
	}
	
	# with folding==i you get idxs belonging to the test set in fold i
	folding<-rep(1:nFolds,length(idxs)/nFolds)

	# create folding
	trainFiles<-rep("",nFolds);
	testFiles<-rep("",nFolds);
	modelFiles<-rep("",nFolds);
	predictionFiles<-rep("", nFolds);
	classoutputFiles<-rep("", nFolds);
	for(i in 1:nFolds) {
		test<-idxs[folding==i];
		train<-idxs[folding!=i];
  
		# test<-sort(test)
		# train<-sort(train)
		# cat("train", train, "\n");
		# cat("test",  test, "\n");  
  
		# in train partition, zero all test labels
		tmp<-dat;
		tmp[test,2]<-0;
		fn<-sprintf("%s/%s-fold%02d_train.csv", foldsFolder, labelFile, i);
		write.table(tmp, file=fn, sep=";", row.names=FALSE, append=FALSE);
		trainFiles[i]<-fn;
		
		# in test partition, zero all train labels
		tmp<-dat;
		tmp[train,2]<-0;
		fn<-sprintf("%s/%s-fold%02d_test.csv", foldsFolder, labelFile, i); 
		write.table(tmp, file=fn, sep=";", row.names=FALSE, append=FALSE);  
		testFiles[i]<-fn;
		

		# model file
		fn<-sprintf("%s/%s-fold%02d_model", modelsFolder, labelFile, i);
		modelFiles[i]<-fn;

		# preduction output
		fn<-sprintf("%s/%s-fold%02d_vote.csv", predictionsFolder, labelFile, i);
		predictionFiles[i]<-fn;
		
		# classifier output
		fn<-sprintf("%s/%s-fold%02d_classoutput.xml", classoutputFolder, labelFile, i);
		classoutputFiles[i]<-fn;	
	}
	folds[[cnt]]<-list();
	folds[[cnt]]$signalFile<-sprintf("%s/%s", datasetFolder, signalFiles[dsetIdx]);		
	folds[[cnt]]$trainFiles<-trainFiles;
	folds[[cnt]]$testFiles<-testFiles;
    folds[[cnt]]$modelFiles<-modelFiles;
    folds[[cnt]]$predictionFiles<-predictionFiles;
    folds[[cnt]]$classoutputFiles<-classoutputFiles;	

	folds[[cnt]]$classes<-classes;
	
	cnt<-cnt+1;
	
	cat("\n")
}

# store info needed by later stages
fn<-sprintf("cross_valid/fold_info.RData");
save(file=fn, "folds", "nFolds");

cat("Done.\n");

