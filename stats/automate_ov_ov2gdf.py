#!/bin/python

import os, glob
import subprocess
import xml.etree.ElementTree as ET

# where signals are recorded, should be one folder per ID, subfolders "mus" and "nomus"
signals_path="../../data"

# command to execute -- better put it in PATH
ov_binary="ov-designer-1.2"
# will be used to fast-forward processing
ov_scenario="../ov2gdf.xml"
# openvibe reads this file to locate the ov file
ov_script_config_input="../ov2gdf_input.cfg"
# and here to write .gdf file
ov_script_config_output="../ov2gdf_output.cfg"


def run_ov():
    p = subprocess.Popen([ov_binary, "--no-gui", "--play-fast", ov_scenario], stdout=subprocess.PIPE)
    # p = subprocess.Popen(["ls", "-l", "/etc/resolv.conf"], stdout=subprocess.PIPE)
    output, err = p.communicate()
    return output, err

# id_path: location of signals for this subject
def process(id_path): 
    # pre and post graz should be located in a dedicated folder
    graz_path = os.path.join(id_path, "graz")
    ov_files = glob.glob(graz_path + '/*.ov')
    for ov in ov_files:
        abs_ov = os.path.abspath(ov)
        print "Processing", abs_ov

        config_ov(ov_script_config_input, abs_ov)
        # the output file will differ only in extention
        abs_gdf = os.path.splitext(abs_ov)[0]+'.gdf'
        config_ov(ov_script_config_output, abs_gdf)

        print "Running OpenViBE"
        output, err = run_ov()
        print "%%% ouput %%%"
        print output
        print "%%% error %%%"
        print err

# point OV conf_file to gdf_file
def config_ov(conf_file, gdf_file):
    tree = ET.parse(conf_file)
    root = tree.getroot()
    # here gdf file is the first parameter
    root[0].text =  gdf_file
    # save back
    tree.write(conf_file)

# there is a folder per between-subject condition
for cond in ["adapt", "noadapt"]:
    for d in os.listdir(signals_path + "/" + cond):
        id_path = os.path.join(signals_path, cond, d)
        # only want folders
        if os.path.isfile(id_path):
            continue
        print "studying ID:",  d
        process(id_path)    



