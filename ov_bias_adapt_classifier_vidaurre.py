import numpy as np
import xml.etree.ElementTree as ET
import datetime
import math, random
from scipy.stats import beta

# Code: Jelena Mladenovic & Jeremy Frey

# Bias (or not) input coming from the classifier. class A should be -1 and class B 1, implementing (roughly) Vidaurre et al. "Toward Unsupervised Adaptation of LDA for Brain-Computer Interfaces"
# FIXME: might not work if input's actual frequency is higher than box's frequency
# NB: based on ov_bias_adapt_classifier.py, based on IBI script from Tobe

# Will take input ("orig"), center it if option set, bias it if option set, and enable/disable

# "Fake output" mode: at each trial will automatically go to a direction or another

# load/write perf between runs, XML format
# E.g. <subject><timestamp>2016-08-05T11:37:36.105328</timestamp><classA><score>200</score><classification>0.3</classification></classA><classB><score>300</score><classification>0.5</classification></classB></subject>
# Use stim configured as "Run start" to reset class output and load values, stim "Run stop" to save data.

# at the moment constants, min and max bias to correct center
MIN_CENTER_BIAS = -0.5
MAX_CENTER_BIAS = 0.5

# 0 (always wrong direction) to 1 (always good direction)
FAKE_ACCURACY = 0.75
# 0 (base is middle) to 1 (base is max value, either -1 or 1)
FAKE_BASE_VALUE = 0.7
# adding gaussian noise at each step
FAKE_NOISE_STD = 0.1
# how often the direction might change depending on accuracy (in seconds)
FAKE_DIRECTION_CHANGE = 0.5
#FIXME: faking depends on sampling rate and chunk size (how often noise is computed)

# for bias beta, range of the possible accuracies (will clip if outside): 
MIN_ACCURACY = 0.5
MAX_ACCURACY = 1
# if cannot load accuracy
DEFAULT_ACCURACY = 0.75
# lower and upper border for the beta functions that will serve as default bias for input (minn to maxx)
# fixed value to have save bias no matter the accuracy
# with 0.33, ratio alpha/beta will be about 0.5
SHIFT_MIN = 0.33 # 0.2
SHIFT_MAX = 0.33 # 0.5

def bias_beta(x, acc=DEFAULT_ACCURACY, negative=False, minn=MIN_ACCURACY, maxx=MAX_ACCURACY, shift_min=SHIFT_MIN, shift_max=SHIFT_MAX):
    """
    x: probability, should be between 0 and 1, in this context classifier output
    acc: influences the strength of the bias; supposed to be classification accuracy of participant during calibration
    negative: set to True to create a negative bias; will inverse alpha and beta and at the same time reverse accuracies
        negative == False: positive bias has more influence over lower accuracies
        negative == True: negative bias has less influence over lower accuracies
    minn:lowest expected value for acc -- e.g. lowest accuracy
    maxx: highest expected value acc -- e.g. highest accuracy
    shift_min, shift_max: lower and upper border for the beta functions that will serve as bias for acc (minn to maxx)
    """
    # safety check
    if acc > maxx:
        acc = maxx
    elif acc < minn:
        acc = minn
    if negative:
        inverse = -1
    else:
        inverse = 1
    # remap change in accuracie to 0..1
    if (maxx == minn):
        remap = 0
    else:
        remap = (acc - minn) / (maxx - minn)
    # will help to re-order input: 0.5 is the middle between 0..1 used in remap
    # if inverse is "1" remap is not changed; if inverse is "-1" 0..1 becomes 1..0
    mid = 0.5
    base = mid + mid * inverse
    reorder =  (base - inverse * remap)
    # shift to desired range
    shift = shift_min + reorder * (shift_max - shift_min)
    # alpha and beta parameters for the beta cumulative distribution function
    a = (1 - shift * inverse) 
    b = (1 + shift * inverse) 
    return beta.cdf(x, a, b)

class MyOVBox(OVBox):
   def __init__(self):
      OVBox.__init__(self)
      self.channelCount = 0
      self.samplingFrequency = 0
      self.epochSampleCount = 0 # should be a divider of self.timeBuffer!
      self.curEpoch = 0
      self.startTime = 0.
      self.endTime = 0.
      self.dimensionSizes = list()
      self.dimensionLabels = list()
      self.timeBuffer = list()
      self.signalBuffer = None
      self.signalHeader = None
      # four variables for four channels...
      self.lastOrigValue = -1
      self.lastCenterValue = -1
      self.lastBiasValue = -1
      self.lastOutputValue = -1
      self.debug = False
      # stims for the studied class and start / stop of run
      self.classAStartStim = 0
      self.classASopStim = 0
      self.classBStartStim = 0
      self.classBStopStim = 0
      self.classRunStartStim = 0
      self.classRunStopStim = 0
      # where to read/save performance data
      self.perfFile = ""
      self.perfFileBackup = ""
      # where to read accuracy data
      self.accFile = ""

      # commands only during trials -- code 1 for class A and 2 for class B; -1 if no current trial
      self.currentClass = -1
      # will not try to bias of no file loaded
      self.gotPreviousRun = False
      # holders for previous data
      self.prevScoreA = 0
      self.prevScoreB = 0
      self.prevClassA_avg = -1
      self.prevClassB_avg = 1
      # holders for current data -- will be reset upon new race (recieving "Run start" stim)
      self.classAValues = np.array([])
      self.classBValues = np.array([])
      self.scoreA = 0
      self.scoreB = 0
      # enable / disable functionalities
      self.enableCenter = False
      self.enableAdapt = False
      self.biasNegative = False
      #  will hold player accuracy
      self.biasAcc = DEFAULT_ACCURACY
      # save/load perf (if disabled will not even gather data about class output)
      self.enablePerf = True
      # will be used to repeatidely print info message about current bias
      self.gotAccuracy = False

      # value to add to current run to center output
      self.biasCenter = 0

   # this time we also re-define the initialize method to directly prepare the header and the first data chunk
   def initialize(self):
      # four channels, original classifier output, possibly recentered with vidaurre, possibly adapted, enabled or not between flag
      self.channelCount = 4
      
      # try get debug flag from GUI
      try:
        debug = (self.setting['Debug']=="true")
      except:
        print "Couldn't find debug flag"
      else:
        self.debug=debug
        
      # flags for enabling / disabling center and adapt biases
      self.enableCenter = (self.setting['Center']=="true")
      self.enableAdapt = (self.setting['Adapt']=="true")
      # if set, will bias negatively in the "adapt" condition
      self.biasNegative = (self.setting['Bias negative']=="true")

      self.enablePerf = (self.setting['Performance computations']=="true")
      self.enableFake = (self.setting['Fake output']=="true")

      # we want our stims
      self.classAStartStim = OpenViBE_stimulation[self.setting['Class A start']]
      self.classAStopStim = OpenViBE_stimulation[self.setting['Class A stop']]
      self.classBStartStim = OpenViBE_stimulation[self.setting['Class B start']]
      self.classBStopStim = OpenViBE_stimulation[self.setting['Class B stop']]
      self.classRunStartStim = OpenViBE_stimulation[self.setting['Class Run start']]
      self.classRunStopStim = OpenViBE_stimulation[self.setting['Class Run stop']]
      self.classACollect = OpenViBE_stimulation[self.setting['Class A collection']]
      self.classBCollect = OpenViBE_stimulation[self.setting['Class B collection']]
      # for 5 points
      self.classACollectStar = OpenViBE_stimulation[self.setting['Class A collection star']]
      self.classBCollectStar = OpenViBE_stimulation[self.setting['Class B collection star']]
      
      # settings are retrieved in the dictionary
      self.samplingFrequency = int(self.setting['Sampling frequency'])
      self.epochSampleCount = int(self.setting['Generated epoch sample count'])
      
      #creation of the signal header
      self.dimensionLabels.append('orig_classifier') 
      self.dimensionLabels.append('centered_classifier') 
      self.dimensionLabels.append('biaised_classifier')
      self.dimensionLabels.append('enabled_classifier') 
      self.dimensionLabels += self.epochSampleCount*['']
      self.dimensionSizes = [self.channelCount, self.epochSampleCount]
      self.signalHeader = OVSignalHeader(0., 0., self.dimensionSizes, self.dimensionLabels, self.samplingFrequency)
      self.output[0].append(self.signalHeader)

      #creation of the first signal chunk
      self.endTime = 1.*self.epochSampleCount/self.samplingFrequency
      self.signalBuffer = np.zeros((self.channelCount, self.epochSampleCount))
      self.updateTimeBuffer()
      self.resetSignalBuffer()
      #will be used for fake
      self.fakeTick = 0
      self.fakeGood = True


      # retrieve filename for performances
      self.perfFile = self.setting['Performance data']
      # this one should possess timestamps in order to create new file each time upon save
      self.perfFileBackup = self.setting['Performance backup']
      # retrieve filename for accuracies
      self.accFile = self.setting['Accuracy data']
      
      # load accuracy data if will adapt
      if self.enableAdapt:
          self.loadAcc()
    
      self.printInfos()

   def printInfos(self):
       print("\t===")
       if self.enableCenter:
           print("\tCenter with biasCenter: %f (foundPerf: %r)" % (self.biasCenter, self.gotPreviousRun))
       if self.enableAdapt and not self.biasNegative:
           print("\tAdapt positive with acc %f (foundAcc: %r, min: %f, max: %f)" % (self.biasAcc, self.gotAccuracy, MIN_ACCURACY, MAX_ACCURACY))
       elif self.enableAdapt and self.biasNegative:
           print("\tAdapt negative with acc %f (foundAcc: %r, min: %f, max: %f)" % (self.biasAcc, self.gotAccuracy, MIN_ACCURACY, MAX_ACCURACY))
       if self.enableFake:
           print("\tFake output")
       print("\t===")
       
   # the center bias that should be applied
   # apply formula to bias current run from previous classifier output (median of each class)
   def setupBias(self):
      if self.gotPreviousRun:
          if math.isnan(self.prevClassA_avg) or  math.isnan(self.prevClassB_avg):
              print("Previous data contains NaN, no bias for now")
          else:
              # 1st class should be -1, second 1, center ideally is 0
              self.biasCenter = (self.prevClassA_avg + self.prevClassB_avg) / 2.0
              # check against min/max
              if self.biasCenter < MIN_CENTER_BIAS:
                  self.biasCenter = MIN_CENTER_BIAS
              elif self.biasCenter > MAX_CENTER_BIAS:
                  self.biasCenter = MAX_CENTER_BIAS
      else:
          print "No data for previous run"

      print "Bias to center output:", self.biasCenter
     
   # read data about accuracy (should be generated by cross-validation R scripts)
   def loadAcc(self):
      print "Loading perfs from:", self.accFile
      # try to read file
      try:
          text_file = open(self.accFile, "r")
      except:
          print "!! Error, opening file !!"
          return
      else:
          raw_xml = text_file.read()
          text_file.close()
      # try to convert to XML
      try:
          xml_root = ET.fromstring(raw_xml)
      except:
          print "!! Error, converting to XML !!"
          return

      # fetching data
      try:
          self.biasAcc = float(xml_root.find('accuracy').text)
      except:
          print "!! Error, parsing XML !!"
          return
      
      print "Found accuracy:", self.biasAcc
      self.gotAccuracy = True
       
   # read data from last run
   def loadPerf(self):
      print "Loading perfs from:", self.perfFile
      # try to read file
      try:
          text_file = open(self.perfFile, "r")
      except:
          print "!! Error, opening file !!"
          return
      else:
          raw_xml = text_file.read()
          text_file.close()
      # try to convert to XML
      try:
          xml_root = ET.fromstring(raw_xml)
      except:
          print "!! Error, converting to XML !!"
          return

      # fetching data
      try:
          self.prevScoreA = float(xml_root.find('classA').find('score').text)
          self.prevScoreB = float(xml_root.find('classB').find('score').text)
          self.prevClassA_avg = float(xml_root.find('classA').find('classification').text)
          self.prevClassB_avg = float(xml_root.find('classB').find('classification').text)
      except:
          print "!! Error, parsing XML !!"
          return

      self.gotPreviousRun = True
      print "Previous scores -- class A:", self.prevScoreA, " - class B:", self.prevScoreB
      print "Previous classifier output -- class A:", self.prevClassA_avg, " - class B:", self.prevClassB_avg
        
   # FIXME: dirty hack, saving as well a backup file
   def savePerf(self):
      print "Saving perfs to:", self.perfFile

      # skip if there is no recorded values for classes
      if (len(self.classAValues) < 1) or  (len(self.classBValues) < 1):
          print("No values for at least one of the classes, skip saving")
          return

      # init xml, add timestamp
      xml_root = ET.Element('subject')
      xml_time = ET.SubElement(xml_root, 'timestamp')
      i = datetime.datetime.now()
      xml_time.text = i.isoformat()
      # setup classA, score and classification
      xml_classA = ET.SubElement(xml_root, 'classA')
      xml_scoreA = ET.SubElement(xml_classA, 'score')
      xml_scoreA.text = str(self.scoreA)
      xml_classA = ET.SubElement(xml_classA, 'classification')
      xml_classA.text = str(np.median(self.classAValues))
      # classB
      xml_classB = ET.SubElement(xml_root, 'classB')
      xml_scoreB = ET.SubElement(xml_classB, 'score')
      xml_scoreB.text = str(self.scoreB)
      xml_classB = ET.SubElement(xml_classB, 'classification')
      xml_classB.text = str(np.median(self.classBValues))
      try:
          text_file = open(self.perfFile, "w+")
      except:
          print "!! Error, writing file !!"
          return
      else:
          text_file.write(ET.tostring(xml_root))
          text_file.close()

          print "New scores -- class A:", xml_scoreA.text, " - class B:", xml_scoreB.text
          print "New classifier output -- class A:", xml_classA.text, " - class B:", xml_classB.text

      print "Saving backup to:", self.perfFileBackup
      try:
          text_file_backup = open(self.perfFileBackup, "w+")
      except:
          print "!! Error, writing backup file !!"
          return
      else:
          text_file_backup.write(ET.tostring(xml_root))
          text_file_backup.close()

   def updateStartTime(self):
      self.startTime += 1.*self.epochSampleCount/self.samplingFrequency

   def updateEndTime(self):
      self.endTime = float(self.startTime + 1.*self.epochSampleCount/self.samplingFrequency)

   def updateTimeBuffer(self):
      self.timeBuffer = np.arange(self.startTime, self.endTime, 1./self.samplingFrequency)

   # fill buffer upon new epoch
   def resetSignalBuffer(self):
      self.signalBuffer[0,:] = self.lastOrigValue
      self.signalBuffer[1,:] = self.lastCenterValue
      self.signalBuffer[2,:] = self.lastBiasValue
      self.signalBuffer[3,:] = self.lastOutputValue


   def sendSignalBufferToOpenvibe(self):
      start = self.timeBuffer[0]
      end = self.timeBuffer[-1] + 1./self.samplingFrequency
      bufferElements = self.signalBuffer.reshape(self.channelCount*self.epochSampleCount).tolist()
      self.output[0].append( OVSignalBuffer(start, end, bufferElements) )

   # called by process for each stim reiceived; update timestamp of last stim
   def trigger(self, stim):
     if self.debug:
       print "Got stim: ", stim.identifier, " date: ", stim.date, " duration: ", stim.duration

     if stim.identifier == self.classAStartStim:
       self.currentClass = 1
       if self.debug:
         print "output class A on"
     elif stim.identifier == self.classBStartStim:   
       self.currentClass = 2
       if self.debug:
         print "output class B on"
     elif stim.identifier == self.classAStopStim or stim.identifier == self.classBStopStim:
       self.currentClass = -1
       if self.debug:
         print "output off"

     # new race, reset class values and scores, load previous data
     elif stim.identifier == self.classRunStartStim:
       self.classAValues = np.array([])
       self.classBValues = np.array([])
       self.scoreA = 0
       self.scoreB = 0
       if self.enablePerf:
           self.loadPerf()
       self.setupBias()
       self.printInfos()
     # race completed, save values
     elif stim.identifier == self.classRunStopStim and self.enablePerf:
       self.savePerf()

     elif stim.identifier == self.classACollect:
       self.scoreA += 1
     elif stim.identifier == self.classBCollect:
       self.scoreB += 1
     elif stim.identifier == self.classACollectStar:
       self.scoreA += 5
     elif stim.identifier == self.classBCollectStar:
       self.scoreB += 5
     
   # clean input values
   def cleanIt(self):
       if self.lastOrigValue < -1:
           self.lastOrigValue = -1
       elif self.lastOrigValue > 1:
           self.lastOrigValue = 1
           
   # apply bias, center based on last run
   # use biasCenter to split input in half, map each half to eihter -1...0 or 0..1
   def centerIt(self):
       # check if option set
       if not self.enableCenter:
           self.lastCenterValue = self.lastOrigValue
           return
           
       # check against odd values
       if self.biasCenter == 1 or self.biasCenter == -1:
           self.lastCenterValue = self.lastOrigValue
           return

       # take care of left side
       if self.lastOrigValue < self.biasCenter:
           inputRange = self.biasCenter + 1
           self.lastCenterValue = (self.lastOrigValue + 1) / inputRange - 1
       # now right side
       elif self.lastOrigValue > self.biasCenter:
           inputRange = 1 - self.biasCenter
           self.lastCenterValue = (self.lastOrigValue - 1) /inputRange + 1      
       # will be centered exactly
       else:
           self.lastCenterValue = 0
             
   # TODO: apply bias toward a target with new formula
   def biasIt(self):
       if not self.enableAdapt:
           self.lastBiasValue = self.lastCenterValue
           return
         
       # bias depending on current class. 1st class is -1; 2nd class is 1
       if self.currentClass > 0:
            # we must remap input differently is the class is -1 or 1
            if self.currentClass == 1:
                reverse = -1
            else:
                reverse = 1           
            # remap to 0..1, with 1 currentClass
            x = ((self.lastCenterValue * reverse) + 1) / 2
            bias = bias_beta(x, self.biasAcc, self.biasNegative)
            # remap to -1 .. 1
            self.lastBiasValue = (bias * 2 - 1) * reverse
       else: # no active class, no bias
           self.lastBiasValue = self.lastCenterValue

       if self.lastBiasValue  < -1:
           self.lastBiasValue = -1
       elif self.lastBiasValue  > 1:
           self.lastBiasValue = 1
   
   # starting a trial, for fake
   def fakeStart(self):
       self.fakeDirection()
       
   # choose one direction or the other when fake is on
   def fakeDirection(self): 
       self.fakeTick = self.getCurrentTime()
       # will it go towardthe right target?
       if (random.random() <  FAKE_ACCURACY):
           self.fakeGood = True
       else:
           self.fakeGood = False
       
   # Will enable / disable last channel depending on trial status -- or just fake the output is option set
   def enableOrFakeIt(self):
       if self.currentClass > 0:
           # fake mode, create value
           if self.enableFake:
               # check if we should change direction
               if self.getCurrentTime() - self.fakeTick > FAKE_DIRECTION_CHANGE:
                   self.fakeDirection()

               # choose direction, first class is -1
               if (self.currentClass == 1 and self.fakeGood) or (self.currentClass == 2 and not self.fakeGood):
                   fakeVal = -1
               else:
                   fakeVal = 1
               # modulate with mean
               fakeVal *= FAKE_BASE_VALUE
               # add gaussian noise
               fakeVal += random.gauss(0, FAKE_NOISE_STD)
               if (fakeVal < -1):
                   fakeVal = -1
               elif (fakeVal > 1):
                   fakeVal = 1
               self.lastOutputValue = fakeVal
           # no fake, just validate bias
           else:
               self.lastOutputValue = self.lastBiasValue
       else:
           self.lastOutputValue = 0

   # called by process each loop or by trigger when got new stimulation;  update output
   def updateValues(self):
     self.signalBuffer[0,self.curEpoch:] = self.lastOrigValue
     self.signalBuffer[1,self.curEpoch:] = self.lastCenterValue
     self.signalBuffer[2,self.curEpoch:] = self.lastBiasValue
     self.signalBuffer[3,self.curEpoch:] = self.lastOutputValue
          
   # the process is straightforward
   def process(self):
      ## Deal with received stimulations
      # we iterate over all the input chunks in the input buffer
      for chunkIndex in range( len(self.input[0]) ):
         # if it's a header... we have to catch it otherwise it'll be seen as OVStimulationSet (??), but that's it
         if(type(self.input[0][chunkIndex]) == OVStimulationHeader):
           self.input[0].pop()
         # we reiceive actual data
         elif(type(self.input[0][chunkIndex]) == OVStimulationSet):
           # create a list for corresponding chunck
           stimSetIn = self.input[0].pop()
           # even without any signals we receive sets, have to check what they hold
           for stim in stimSetIn:
             # check which 
             self.trigger(stim)
         # useless?
         elif(type(self.input[0][chunkIndex]) == OVStimulationEnd):
           self.input[0].pop()

      ## deal with classifier input -- copying and saving value
      for chunk_index in range(len(self.input[1])):
            #passing on the header to the output
            if(type(self.input[1][chunk_index]) == OVStreamedMatrixHeader):
                self.input[1].pop()
            #biasing the input signal to output it
            elif(type(self.input[1][chunk_index]) == OVStreamedMatrixBuffer):
                inputChunk = self.input[1].pop()
                # using last value of current input
                self.lastOrigValue = inputChunk[-1]
                self.cleanIt()
                # add to past values to the list if a trial is currently on
                if self.currentClass == 1 and self.enablePerf:
                    self.classAValues = np.append(self.classAValues, self.lastOrigValue)
                elif self.currentClass == 2 and self.enablePerf:
                    self.classBValues = np.append(self.classBValues, self.lastOrigValue)


      # compute bias, copy values to output
      self.centerIt()
      self.biasIt()
      self.enableOrFakeIt()
      self.updateValues()
      
      # update timestamps
      #start = self.timeBuffer[0]
      end = self.timeBuffer[-1]
      while self.curEpoch < self.epochSampleCount and self.getCurrentTime() >= self.timeBuffer[self.curEpoch]:
         self.curEpoch+=1
      # send values      
      if self.getCurrentTime() >= end:
         # send buffer
         self.sendSignalBufferToOpenvibe()
         self.updateStartTime()
         self.updateEndTime()
         self.updateTimeBuffer()
         self.resetSignalBuffer()
         self.curEpoch = 0

   # this time we also re-define the uninitialize method to output the end chunk.
   def uninitialize(self):
      end = self.timeBuffer[-1]
      self.output[0].append(OVSignalEnd(end, end))

box = MyOVBox()
