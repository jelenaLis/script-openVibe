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
list_cond = [] # 0 for nomus, 1 for mus conditions
list_direction = [] # 0 for left, 1 for right
list_score = []
list_class = []


def run_ov():
    p = subprocess.Popen([ov_binary, "--no-gui", "--play-fast", ov_scenario], stdout=subprocess.PIPE)
    # p = subprocess.Popen(["ls", "-l", "/etc/resolv.conf"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    return output, err

# taken from adapt script, maybe simpler to use all of ET power (see config_ov)
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

# id_path: location of signals for this subject
# condition_tag: "mus" or "nomus", subfolders
def process(id_path, condition_tag):
    global list_id, list_cond, list_direction, list_score, list_class
    
    mus_path = os.path.join(id_path, condition_tag)
    class_files = glob.glob(mus_path + '/*class.gdf')
    for gdf in class_files:
        abs_gdf = os.path.abspath(gdf)
        print "Processing", abs_gdf

        config_ov(ov_script_config, abs_gdf)

        print "Running OpenViBE"
        output, err = run_ov()
        print "%%% ouput %%%"
        print output
        print "%%% error %%%"
        print err

        print "Getting parameters"
        prevScoreA, prevScoreB, prevClassA_avg, prevClassB_avg  = loadPerf(ov_script_res)

        list_id.append(d)
        list_cond.append(condition_tag)
        # left then right
        list_direction.append(0)
        list_score.append(prevScoreA)
        list_class.append(prevClassA_avg)
        list_direction.append(1)
        list_score.append(prevScoreB)
        list_class.append(prevClassB_avg)
    
# point OV conf_file to gdf_file
def config_ov(conf_file, gdf_file):
    tree = ET.parse(conf_file)
    root = tree.getroot()
    # here gdf file is the first parameter
    root[0].text =  gdf_file
    # save back
    tree.write(conf_file)
    
for d in os.listdir(signals_path):
    id_path = os.path.join(signals_path, d)
    # only want folders
    if os.path.isfile(id_path):
        continue
    print "studying ID:",  d

    # deal with music
    process(id_path, "mus")    
    # deal with nomusic
    process(id_path, "nomus")    


print "ID:", list_id
print "Conditions:", list_cond
print "Directions:", list_direction
print "Scores:", list_score
print "Classes", list_class

