import numpy, sys, os
from math import ceil
# retrieve LSL library compiled by OpenViBE
# FIXME: not working??
#ov_lib_path = os.getcwd() + "./lib_ov/"
#sys.path.append(ov_lib_path)
# FIXME absolute path to point to pylsl.py & liblsl.so -- added before any other LSL path
sys.path = ["/home/jfrey/flow/script-openVibe/libs2"] + sys.path

from pylsl import StreamInlet, resolve_stream

# NB: if case of several streams and/or several channels, every stim will be concatenated

# let's define a new box class that inherits from OVBox
class MyOVBox(OVBox):
  def __init__(self):
    OVBox.__init__(self)

    
  # the initialize method reads settings and outputs the first header
  def initialize(self):
    self.debug=self.setting['debug'] == "true"
    print "Debug: ", self.debug
    self.stream_type=self.setting['Stream type']
    # total channels for all streams
    self.channelCount = 0
    
    all_streams = self.setting['Get all streams'] == "true"
    
    self.overcomeCheck = self.setting['Overcome code check'] == "true"
     
    self.stream_name=self.setting['Stream name'] # in case !all_streams
    
    print "Looking for streams of type: " + self.stream_type
    
    streams = resolve_stream('type',self.stream_type)
    print "Nb streams: " + str( len(streams))
    
    if not all_streams:
      print "Will only select (first) stream named: " + self.stream_name
      self.nb_streams = 1
    else:
      self.nb_streams = len(streams)

    # create inlets to read from each stream
    self.inlets = []
    # retrieve also corresponding StreamInfo for future uses (eg sampling rate)
    self.infos = []
    
    # save inlets and info + build signal header
    for stream in streams:
      # do not set max_buflen because we *should not* be spammed by values
      inlet = StreamInlet(stream, max_buflen=1)
      info = inlet.info()
      name = info.name()
      print "Stream name: " + name
      # if target one stream, ignore false ones
      if not all_streams and name != self.stream_name:
        continue
      print "Nb channels: " + str(info.channel_count())
      self.channelCount += info.channel_count()
      stream_freq = info.nominal_srate()
      print "Sampling frequency: " + str(stream_freq)
      if  stream_freq != 0:
        print "WARNING: Wrong stream?"
      
      self.inlets.append(inlet)
      self.infos.append(info)
      
      # if we're still here when we target a stream, it means we foand it
      if not all_streams:
        print "Found target stream"
        break

    # we need at least one stream before we let go
    if self.channelCount <= 0:
      raise Exception("Error: no stream found.")
    
    # we append to the box output a stimulation header. This is just a header, dates are 0.
    self.output[0].append(OVStimulationHeader(0., 0.))
      
  # The process method will be called by openvibe on every clock tick
  def process(self):
    # A stimulation set is a chunk which starts at current time and end time is the time step between two calls
    # init here and filled within triger()
    self.stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
    
    # read all available stream
    for inlet in self.inlets:
      samples = []
      # pull everything we can from all channel
      sample,timestamp = inlet.pull_sample(0)
      while sample != None:
        # for each valid sample, add it to list
        samples += sample
        sample,timestamp = inlet.pull_sample(0)
      
      # every value will be converted to openvibe code and a stim will be create
      for label in samples: 
        label = str(label)
        if self.debug:
          print "Got label: ", label
        # we get the corresponding code using the OpenViBE_stimulation dictionnary
        try:
          stimCode = OpenViBE_stimulation[label]
        # an exception means lookup failed in dict label:code
        except:
          # no openvibe label, may be over passed by option
          if self.overcomeCheck:
            if self.debug:
              print "Cannot get corresponding code, overcome with code: " + label
            self.stimSet.append(OVStimulation(float(label), self.getCurrentTime(), 0.))
          else:
            if self.debug:
              print "Cannot get corresponding code, ignoring"
        # at this point we got a stimulation
        else:
          if self.debug:
            print "Corresponding code: ", stimCode
          # the date of the stimulation is simply the current openvibe time when calling the box process
          self.stimSet.append(OVStimulation(stimCode, self.getCurrentTime(), 0.))
    
    # even if it's empty we have to send stim list to keep the rest in sync
    self.output[0].append(self.stimSet)

  def uninitialize(self):
    # we send a stream end.
    end = self.getCurrentTime()
    self.output[0].append(OVStimulationEnd(end, end))
    for inlet in self.inlets:
      inlet.close_stream()

box = MyOVBox()
