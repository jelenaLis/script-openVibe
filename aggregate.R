# Aggregates crossvalidation results
# jtlindgren feb2015

rm(list=ls())

# the one external dependency
require(XML)

#g_ResultsFile<-"experiment_info.RData";
g_ResultsFile<-"cross_valid/fold_info.RData";

#### should be nothing to modify below this

load(file=g_ResultsFile);

accuracies<-rep(0,length(folds));
confidences<-rep(0,length(folds));
# will hold mean per class across folds for each (i.e. here, 1) dataset
meansA<-rep(0,length(folds));
meansB<-rep(0,length(folds));

for(dsetIdx in 1:length(folds))
{
	cat("Dataset [", folds[[dsetIdx]]$signalFile, "]...\n");
	
	for(foldIdx in 1:length(folds[[dsetIdx]]$predictionFiles))
	{
		# data about classification
		fn<-folds[[dsetIdx]]$predictionFiles[foldIdx];
		dat<-read.table(fn, sep=",")
		if(foldIdx==1) {
			mat<-dat;
		} else {
			mat<-rbind(mat,dat);
		}
		
		# data about classification
		fn<-folds[[dsetIdx]]$classoutputFiles[foldIdx];
                # retrieve median output for class A (left) and B (right)
		classA <- as.numeric(xmlValue(xmlRoot(xmlParse(file=fn))[["classA"]][["classification"]]))
		classB <- as.numeric(xmlValue(xmlRoot(xmlParse(file=fn))[["classB"]][["classification"]]))
		if(foldIdx==1) {
			classAs<-c(classA);
			classBs<-c(classB);
		} else {
			classAs<-c(classAs, classA);
			classBs<-c(classBs, classB);
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
	meansA[dsetIdx]<-mean(classAs);
	meansB[dsetIdx]<-mean(classBs);


	cat("Confusion matrix...\n");
	print(conf	);
	cat("Normalized to accuracy in [0,1]...\n");
	print(normConf);
	cat("Medians output for first class...\n");
	print(classAs);
	cat("Medians output for second class...\n");
	print(classBs);
}

cat("Accuracies per dataset: ", accuracies, "\n")

cat("Mean of accs: ", mean(accuracies), ", var ", var(accuracies), "\n")

cat("Mean of confidences: ", mean(confidences), ", var " , var(confidences), "\n");

cat("Means of classifier outputs for first class: ", meansA, "\n");

cat("Means of classifier output for second class: ", meansB, "\n");


