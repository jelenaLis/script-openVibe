import numpy
from Tkinter import *

# ripoff from the regular version, here only one channel shown, keep parameters but do not use maxValue
# TODO: merge with regular...

class MyOVBox(OVBox):
   def __init__(self):
      OVBox.__init__(self)
      self.channelCount = 0
      self.samplingFrequency = 0
      self.epochSampleCount = 0
      self.minValue = 0
      self.startTime = 0.
      self.endTime = 0.
      self.dimensionSizes = list()
      self.dimensionLabels = list()
      self.timeBuffer = list()
      self.signalBuffer = None
      self.signalHeader = None
      self.windowTitle = "Control channel"

   # this time we also re-define the initialize method to directly prepare the header and the first data chunk
   def initialize(self):
      # one channel for min, another for max
      self.channelCount = 1
           
      # settings are retrieved in the dictionary
      self.samplingFrequency = int(self.setting['Sampling frequency'])
      self.epochSampleCount = int(self.setting['Generated epoch sample count'])
      self.minValue = float(self.setting['min value'])
      self.maxValue = float(self.setting['max value'])
      # retrieve window title in any
      if ("window title" in self.setting) and (self.setting['window title'] != ""):
         self.windowTitle = self.setting['window title']
         
      #creation of the signal header
      self.dimensionLabels.append('Min value')
      self.dimensionLabels.append('Max value')     
      self.dimensionLabels += self.epochSampleCount*['']
      self.dimensionSizes = [self.channelCount, self.epochSampleCount]
      self.signalHeader = OVSignalHeader(0., 0., self.dimensionSizes, self.dimensionLabels, self.samplingFrequency)
      self.output[0].append(self.signalHeader)

      #creation of the first signal chunk
      self.endTime = 1.*self.epochSampleCount/self.samplingFrequency
      self.signalBuffer = numpy.zeros((self.channelCount, self.epochSampleCount))
      self.updateTimeBuffer()
      self.updateSignalBuffer()
      
      #gui
      paramInterval = (self.maxValue - self.minValue) / 5 # for slider graduation, 10th of min-max range
      self.GUImaster = Tk()
      self.GUImaster.title(self.windowTitle)
      # compute range
      range_values = abs(self.maxValue - self.minValue)
      # then median
      medium = range_values/2
      # to widen range we substract/add median to min/max
      bottom = self.minValue - medium
      top = self.maxValue + medium
      
      self.GUISliderMin = Scale(self.GUImaster, label='Value', length=800, from_=bottom, to=top, resolution = 0.001, orient=HORIZONTAL, tickinterval=paramInterval)
      self.GUISliderMin.pack()
 
      self.GUISliderMin.set(self.minValue)

   def updateFromGUI(self):
     self.minValue = self.GUISliderMin.get()
     
   def updateStartTime(self):
      self.startTime += 1.*self.epochSampleCount/self.samplingFrequency

   def updateEndTime(self):
      self.endTime = float(self.startTime + 1.*self.epochSampleCount/self.samplingFrequency)

   def updateTimeBuffer(self):
      self.timeBuffer = numpy.arange(self.startTime, self.endTime, 1./self.samplingFrequency)

   def updateSignalBuffer(self):
      self.signalBuffer[0,:] = self.minValue

   def sendSignalBufferToOpenvibe(self):
      start = self.timeBuffer[0]
      end = self.timeBuffer[-1] + 1./self.samplingFrequency
      bufferElements = self.signalBuffer.reshape(self.channelCount*self.epochSampleCount).tolist()
      self.output[0].append( OVSignalBuffer(start, end, bufferElements) )

   # the process is straightforward
   def process(self):
      start = self.timeBuffer[0]
      end = self.timeBuffer[-1]
      if self.getCurrentTime() >= end:
         # update GUI
         self.GUImaster.update()
         # retrieve values
         self.updateFromGUI()
         # deal with data
         self.sendSignalBufferToOpenvibe()
         self.updateStartTime()
         self.updateEndTime()
         self.updateTimeBuffer()
         self.updateSignalBuffer()

   # this time we also re-define the uninitialize method to output the end chunk.
   def uninitialize(self):
      end = self.timeBuffer[-1]
      self.output[0].append(OVSignalEnd(end, end))
      # detroy GUI
      self.GUImaster.destroy()

box = MyOVBox()
