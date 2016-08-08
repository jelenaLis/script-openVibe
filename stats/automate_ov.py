#!/bin/python

import os, glob

# where signals are recorded, should be one folder per ID, subfolders "mus" and "nomus"
signals_path="../script-openVibe/signals"

# data frame of the poor
list_id = []
list_mus_score_L = []
list_nomus_score_R = []
list_mus_class_L = []
list_mus_class_R = []

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

#onlyfiles = [f for f in listdir(signals_path) if isfile(join(signals_path, f))]
