####
#### Aggregates crossvalidation results
####
#### See README.txt
#####
#### jtlindgren feb2015
####

rm(list=ls())

#g_ResultsFile<-"experiment_info.RData";
g_ResultsFile<-"fold_info.RData";

#### should be nothing to modify below this

load(file=g_ResultsFile);

accuracies<-rep(0,length(folds));
confidences<-rep(0,length(folds));
for(dsetIdx in 1:length(folds))
{
	cat("Dataset [", folds[[dsetIdx]]$signalFile, "]...\n");
	
	for(foldIdx in 1:length(folds[[dsetIdx]]$predictionFiles))
	{
		fn<-folds[[dsetIdx]]$predictionFiles[foldIdx];
		dat<-read.table(fn, sep=",")
		if(foldIdx==1) {
			mat<-dat;
		} else {
			mat<-rbind(mat,dat);
		}	
	}

	classes<-folds[[dsetIdx]]$classes;
	conf<-matrix(data=0,nrow=length(classes),ncol=length(classes));
	confid<-matrix(data=0,nrow=dim(mat)[1],ncol=1);
	#overConfidence<-matrix(data=0,nrow=dim(mat)[1]);
	for(i in 1:dim(mat)[1]) {
		targetClass<-which(classes==mat[i,2]);
		predictedClass<-which(classes==mat[i,3]);
		
		confid[i] <- mat[i,4] / mat[i,5];
	
		conf[targetClass,predictedClass] <- conf[targetClass,predictedClass]+1;
	}

	normConf<-conf;
	for(i in 1:length(classes)) {
		normConf[i,]<-normConf[i,]/sum(normConf[i,])
	}

	confidences[dsetIdx]<-mean(confid);
	
	accuracies[dsetIdx]<-sum(diag(conf))/sum(conf);
	
	cat("Confusion matrix...\n");
	print(conf	);
	cat("Normalized to accuracy in [0,1]...\n");
	print(normConf);
}

cat("Accuracies per dataset: ", accuracies, "\n")

cat("Mean of accs: ", mean(accuracies), ", var ", var(accuracies), "\n")

cat("Mean of confidences: ", mean(confidences), ", var " , var(confidences), "\n");



