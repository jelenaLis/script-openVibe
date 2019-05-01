
# from https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html
from scipy.stats import beta
import matplotlib.pyplot as plt
import numpy as np

# will be used to loop on colors
jet= plt.get_cmap('jet')
colors = iter(jet(np.linspace(0,1,10)))

# plot
fig, ax = plt.subplots(1, 1) 

# discrete points
x = np.linspace(0, 1, 1000)

# base , will define min assistance (for those with accracies 1)
#base = 0.2
shift = 0.2
# "factor", will define how much the assistance varies between accuracies
# 1: won't change between accuracyies
# 0.5: add half between accuracy and target in the formula
# 0: simplest formula, a = c/t and b = t/c
#  < 0:  help even more small accuracies
# > 1: impede more low accuracies
#f = 0.5
density = 0.5

# set to -1 to inverse alpha and beta and at the same time reverse accuracies
# positive bias has more influence over lower accuracies
# negative bias has less influence over lower accuracies
inverse = 1

# FIXME: use minn and maxx as range between "shift" and ???. At the moment touching minn or maxx will shift the whole fuction.
# lowest expected value -- e.g. lowest accuracy
minn = 0.5
# highest expected value -- e.g. highest accuracy
maxx = 1


for c in np.linspace(minn, maxx, 10):
    mid = (minn + maxx) / 2
    base = mid - minn + mid * inverse
    # positif: max == 1
    # negatif: max == -0.5
    cbis =  ((base - inverse * c) * density + shift) 
    
    a = (1 - cbis * inverse) 
    b = (1 + cbis * inverse)
    ax.plot(x, beta.cdf(x, a, b),  color=next(colors))

