# testing various values for the bias function, based on beta cumulative distribution function
from scipy.stats import beta

def bias_beta(x, acc, minn, maxx, shift_min, shift_max, inverse):
    # remap input to 0..1
    if (maxx == minn):
        remap = 0
    else:
        remap = (acc - minn) / (maxx - minn)
    # will help to re-order input: 0.5 is the middle between 0..1 used in remap
    # if inverse is "1" remap is not changed; if inverse is "-1" 0..1 becomes 1..0
    mid = 0.5
    base = mid + mid * inverse
    reorder =  (base - inverse * remap)
    # shift to desired range
    shift = shift_min + reorder * (shift_max - shift_min)
    # alpha and beta parameters for the beta cumulative distribution function
    a = (1 - shift * inverse) 
    b = (1 + shift * inverse) 
    return beta.cdf(x, a, b)

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # lowest expected value -- e.g. lowest accuracy
    minn = 0.5
    # highest expected value -- e.g. highest accuracy
    maxx = 1
    
    # lower and upper border for the beta functions that will serve as bias for input (minn to maxx)
    # fixed value to have save bias no matter the accuracy
    # with 0.33, ratio alpha/beta will be about 0.5
    shift_min = 0.33 # 0.2
    shift_max = 0.33 # 0.5
    
    # set to -1 to inverse alpha and beta and at the same time reverse accuracies
    # positive bias has more influence over lower accuracies
    # negative bias has less influence over lower accuracies
    inverse = 1
    
    # TODO: interpret  effect of inverse values different from 1 and -1
    # TODO: also add parameter for the base value of alpha and beta? (i.e. "1" at the moment, see below)
    
    # how many values to test
    nb_val = 10
    
    # will be used to loop on colors
    jet= plt.get_cmap('jet')
    colors = iter(jet(np.linspace(0,1,nb_val)))
    
    # plot
    fig, ax = plt.subplots(1, 1) 
    
    #  create discrete points for plotting
    x = np.linspace(0, 1, 1000)
    
    # test accuracy of participant
    for acc in np.linspace(minn, maxx, nb_val):
        ax.plot(x, bias_beta(x, acc, minn, maxx, shift_min, shift_max, inverse),  color=next(colors))
