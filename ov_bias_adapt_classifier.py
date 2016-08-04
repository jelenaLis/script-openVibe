import numpy
import xml.etree.ElementTree as ET


# Bias (or not) input coming from the classifier
# FIXME: might not work if input's actual frequency is higher than box's frequency
# NB: based on IBI script from Tobe

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
      # two variables for two channels...
      self.lastOrigValue = -1
      self.lastBiaisedValue = -1
      self.debug = False
      # stims for the studied class and start / stop of run
      self.classAStartStim = 0
      self.classAStopStim = 0
      self.classBStartStim = 0
      self.classBStopStim = 0
      self.classRunStartStim = 0
      self.classRunStopStim = 0
      # where to read/save performance data
      self.perfFile = ""
      # commandes only during trials
      self.enableOutput = False

   # this time we also re-define the initialize method to directly prepare the header and the first data chunk
   def initialize(self):
      # two channels, original classifier output  and biaised output
      self.channelCount = 2
      
      # try get debug flag from GUI
      try:
        debug = (self.setting['Debug']=="true")
      except:
        print "Couldn't find debug flag"
      else:
        self.debug=debug

      # we want our stims
      self.classAStartStim = OpenViBE_stimulation[self.setting['Class A start']]
      self.classAStopStim = OpenViBE_stimulation[self.setting['Class A stop']]
      self.classBStartStim = OpenViBE_stimulation[self.setting['Class B start']]
      self.classBStopStim = OpenViBE_stimulation[self.setting['Class B stop']]
      self.classRunStartStim = OpenViBE_stimulation[self.setting['Class Run start']]
      self.classRunStopStim = OpenViBE_stimulation[self.setting['Class Run stop']]

      # settings are retrieved in the dictionary
      self.samplingFrequency = int(self.setting['Sampling frequency'])
      self.epochSampleCount = int(self.setting['Generated epoch sample count'])
      
      #creation of the signal header
      self.dimensionLabels.append('orig_classifier') 
      self.dimensionLabels.append('biaised_classifier') 
      self.dimensionLabels += self.epochSampleCount*['']
      self.dimensionSizes = [self.channelCount, self.epochSampleCount]
      self.signalHeader = OVSignalHeader(0., 0., self.dimensionSizes, self.dimensionLabels, self.samplingFrequency)
      self.output[0].append(self.signalHeader)

      #creation of the first signal chunk
      self.endTime = 1.*self.epochSampleCount/self.samplingFrequency
      self.signalBuffer = numpy.zeros((self.channelCount, self.epochSampleCount))
      self.updateTimeBuffer()
      self.resetSignalBuffer()

      # retrieve filename for performances
      self.perfFile = self.setting['Performance data']

   def loadPerf(self):
      print "Loading perfs from:", self.perfFile

   def savePerf(self):
      print "Saving perfs to:", self.perfFile
      
   def updateStartTime(self):
      self.startTime += 1.*self.epochSampleCount/self.samplingFrequency

   def updateEndTime(self):
      self.endTime = float(self.startTime + 1.*self.epochSampleCount/self.samplingFrequency)

   def updateTimeBuffer(self):
      self.timeBuffer = numpy.arange(self.startTime, self.endTime, 1./self.samplingFrequency)

   # fill buffer upon new epoch
   def resetSignalBuffer(self):
      self.signalBuffer[0,:] = self.lastOrigValue
      self.signalBuffer[1,:] = self.lastBiaisedValue

   def sendSignalBufferToOpenvibe(self):
      start = self.timeBuffer[0]
      end = self.timeBuffer[-1] + 1./self.samplingFrequency
      bufferElements = self.signalBuffer.reshape(self.channelCount*self.epochSampleCount).tolist()
      self.output[0].append( OVSignalBuffer(start, end, bufferElements) )

   # called by process for each stim reiceived; update timestamp of last stim
   def trigger(self, stim):
     if self.debug:
       print "Got stim: ", stim.identifier, " date: ", stim.date, " duration: ", stim.duration
     if stim.identifier == self.classAStartStim or stim.identifier == self.classBStartStim:
       self.enableOutput = True
       if self.debug:
         print "output on"
     elif stim.identifier == self.classAStopStim or stim.identifier == self.classBStopStim:
       self.enableOutput =  False
       if self.debug:
         print "output off"
     elif stim.identifier == self.classRunStartStim:
       self.loadPerf()
     elif stim.identifier == self.classRunStopStim:
       self.savePerf()

   def biasIt(self):
     if self.enableOutput:   
       self.lastBiasValue = self.lastOrigValue
     else:
       self.lastBiasValue = 0
     
   # called by process each loop or by trigger when got new stimulation;  update output
   def updateValues(self):
     self.signalBuffer[0,self.curEpoch:] = self.lastOrigValue
     self.signalBuffer[1,self.curEpoch:] = self.lastBiasValue

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
           nb_stim =  str(len(stimSetIn))
           for stim in stimSetIn:
             # check which 
             self.trigger(stim)
         # useless?
         elif(type(self.input[0][chunkIndex]) == OVStimulationEnd):
           self.input[0].pop()

      ## deal with classifier input
      for chunk_index in range(len(self.input[1])):
            #passing on the header to the output
            if(type(self.input[1][chunk_index]) == OVStreamedMatrixHeader):
                self.input[1].pop()
            #biasing the input signal to output it
            elif(type(self.input[1][chunk_index]) == OVStreamedMatrixBuffer):
                inputChunk = self.input[1].pop()
                # using last value of current input
                # FIXME: nothing proof!
                self.lastOrigValue = inputChunk[-1]

      # compute bias, copy values to output
      self.biasIt()
      self.updateValues()
      
      # update timestamps
      start = self.timeBuffer[0]
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
