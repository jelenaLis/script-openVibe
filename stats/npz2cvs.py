# will convert output from automate_ov.py to CSV file

import numpy as np

input_file="data.npz"
output_file="data.csv"
CSV_DELIMITER = ","

npzfile = np.load(input_file)

headers = "" 
meta = []

for f in npzfile.files:
    print f
    # we do not check that, but should be same length for each array
    print len(npzfile[f])
    print npzfile[f]
    # adding columns to headers and data
    if len(headers) == 0:
        headers = f
    else:
        headers = headers + CSV_DELIMITER + f

    meta.append(npzfile[f])

#print meta
np.savetxt(output_file, np.array(meta).transpose(), delimiter=CSV_DELIMITER, header=headers, fmt="%s")
