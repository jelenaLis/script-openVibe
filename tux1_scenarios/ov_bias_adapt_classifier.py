import numpy as np
import xml.etree.ElementTree as ET
import datetime
import os.path
from math import exp

# Bias (or not) input coming from the classifier. class A should be -1 and class B 1
# FIXME: might not work if input's actual frequency is higher than box's frequency
# NB: based on IBI script from Tobe

# load/write perf between runs, XML format
# E.g. <subject><timestamp>2016-08-05T11:37:36.105328</timestamp><classA><score>200</score><classification>0.3</classification></classA><classB><score>300</score><classification>0.5</classification></classB></subject>

# FIXME: in the end this version does not used previous data, switch from online_magic() to magic() in biasIt() to do so.

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
      self.classASopStim = 0
      self.classBStartStim = 0
      self.classBStopStim = 0
      self.classRunStartStim = 0
      self.classRunStopStim = 0
      # where to read/save performance data
      self.perfFile = ""
      # commands only during trials -- code 1 for class A and 2 for class B; -1 if no current trial
      self.currentClass = -1
      # will not try to bias of no file loaded
      self.gotPreviousRun = False
      # holders for previous data
      self.prevScoreA = 0
      self.prevScoreB = 0
      self.prevClassA_avg = 0
      self.prevClassB_avg = 0
      # holders for current data
      self.classAValues = np.array([])
      self.classBValues = np.array([])
      self.scoreA = 0
      self.scoreB = 0

      # value to add to current run
      self.biasA = 0
      self.biasB = 0

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
      self.classACollect = OpenViBE_stimulation[self.setting['Class A collection']]
      self.classBCollect = OpenViBE_stimulation[self.setting['Class B collection']]

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
      self.signalBuffer = np.zeros((self.channelCount, self.epochSampleCount))
      self.updateTimeBuffer()
      self.resetSignalBuffer()

      # retrieve filename for performances
      self.perfFile = self.setting['Performance data']

   # dirty fix for real time bias
   def online_magic(self, class_output):
      return class_output + ( 0.79 - class_output)/2.

   # the magical formula, taking a classifier output and giving the bias to apply
   def magic(self, class_avg):
      x = class_avg
      # expected output
      y = x + ( 0.79 - x) * 1/(1+exp(-2*x))
      return y - class_avg

   # the bias that should be applied
   # apply formula to bias current run from previous classifier output
   def setupBias(self):
      if self.gotPreviousRun:
          # 1st class is -1
          self.biasA = -1 * self.magic(self.prevClassA_avg * -1)
          # 2nd class more readable
          self.biasB =  self.magic(self.prevClassB_avg)
      else:
          print "No data for previous run"

      print "Bias for class A:", self.biasA
      print "Bias for class B:", self.biasB
       
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
          
   def savePerf(self):
      print "Saving perfs to:", self.perfFile

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
      xml_classA.text = str(np.average(self.classAValues))
      # classB
      xml_classB = ET.SubElement(xml_root, 'classB')
      xml_scoreB = ET.SubElement(xml_classB, 'score')
      xml_scoreB.text = str(self.scoreB)
      xml_classB = ET.SubElement(xml_classB, 'classification')
      xml_classB.text = str(np.average(self.classBValues))
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
          

   def updateStartTime(self):
      self.startTime += 1.*self.epochSampleCount/self.samplingFrequency

   def updateEndTime(self):
      self.endTime = float(self.startTime + 1.*self.epochSampleCount/self.samplingFrequency)

   def updateTimeBuffer(self):
      self.timeBuffer = np.arange(self.startTime, self.endTime, 1./self.samplingFrequency)

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

     elif stim.identifier == self.classRunStartStim:
       self.loadPerf()
       self.setupBias()
     elif stim.identifier == self.classRunStopStim:
       self.savePerf()


     elif stim.identifier == self.classACollect:
       self.scoreA += 1
     elif stim.identifier == self.classBCollect:
       self.scoreB += 1
       
   def biasIt(self):
     if self.currentClass > 0:   
       if self.currentClass == 1: #1st class is -1
           self.lastBiasValue = -1*self.online_magic(-1*self.lastOrigValue)
       else:
           self.lastBiasValue = self.online_magic(self.lastOrigValue)
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

      ## deal with classifier input -- copying and saving value
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
                # add to past values to the list if a trial is currently on
                if self.currentClass == 1:
                    self.classAValues = np.append(self.classAValues, self.lastOrigValue)
                elif self.currentClass == 2:
                    self.classBValues = np.append(self.classBValues, self.lastOrigValue)

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
