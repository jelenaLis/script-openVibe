#!/bin/python

import os, glob
import subprocess
import xml.etree.ElementTree as ET

# where signals are recorded, should be one folder per ID, subfolders "mus" and "nomus"
signals_path="../signals"

# command to execute -- better put it in PATH
ov_binary="ov-designer-1.2"
# will be used to fast-forward processing
ov_scenario="../replayer_adapt.xml"
# openvibe reads this file to locate data
ov_script_config="../replayer_adapt_gdf.cfg"
# and write there
ov_script_res="../run_perfs_replay.cfg"

# data frame of the poor
list_id = []
list_mus_score_L = []
list_nomus_score_R = []
list_mus_class_L = []
list_mus_class_R = []


def run_ov():
    p = subprocess.Popen([ov_binary, "--no-gui", "--play-fast", ov_scenario], stdout=subprocess.PIPE)
    # p = subprocess.Popen(["ls", "-l", "/etc/resolv.conf"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    return output, err


def loadPerf(res_file):
      print "Loading perfs from:", res_file
      # try to read file
      try:
          text_file = open(res_file, "r")
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
          prevScoreA = float(xml_root.find('classA').find('score').text)
          prevScoreB = float(xml_root.find('classB').find('score').text)
          prevClassA_avg = float(xml_root.find('classA').find('classification').text)
          prevClassB_avg = float(xml_root.find('classB').find('classification').text)
      except:
          print "!! Error, parsing XML !!"
          return

      print "Scores -- class A:", prevScoreA, " - class B:", prevScoreB
      print "Classifier output -- class A:", prevClassA_avg, " - class B:", prevClassB_avg

      return prevScoreA, prevScoreB, prevClassA_avg, prevClassB_avg


for d in os.listdir(signals_path):
    id_path = os.path.join(signals_path, d)
    # only want folders
    if os.path.isfile(id_path):
        continue
    print "studying ID:",  d
    # deal with music
    mus_path = os.path.join(id_path, "mus")
    class_files = glob.glob(mus_path + '/*class.gdf')
    for gdf in class_files:
        abs_gdf = os.path.abspath(gdf)
        print "Processing", abs_gdf
    #"for m in os.listdir(signals_path):

    nomus_path = os.path.join(id_path, "nomus")


#output, err = run_ov()

#print "%%% ouput %%%"
#print output
#print "%%% error %%%"
#print err

print loadPerf(ov_script_res)

