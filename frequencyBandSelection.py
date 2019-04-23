# -*- coding: utf-8 -*-
##
##   [2017] Fabien Lotte - Inria
##

from __future__ import print_function, division
import numpy as np
#import matplotlib.pyplot as plt

class FrequencyBandSelectionBox(OVBox):
    def __init__(self):
        super(FrequencyBandSelectionBox, self).__init__()
        self.num_channels  = 0
        self.sampling_rate = 0
        self.num_samples   = 0
        self.last_time     = 0
        self.stimulations  = []
        self.currentLabel  = -1
        self.labels        = []
        self.nbTrainData   = 0
        self.outputStimCode = 33287; #code for output stimulation 'OVTK_StimulationId_TrainCompleted'

    def initialize(self):
        assert len(self.input)  == 2,  'This box needs exactly 2 input'
        assert len(self.output) == 1,   'This box needs exactly 1 output'
        
        stim_label1 = self.setting['Class 1 stimulation label']
        stim_label2 = self.setting['Class 2 stimulation label']
        stim_train = self.setting['Train Stimulation']
        self.minFreq  = int(self.setting['MinFrequency'])
        self.maxFreq  = int(self.setting['MaxFrequency'])
        self.filename = self.setting['Output config filename']
        self.codeClass1 = OpenViBE_stimulation[stim_label1]
        self.codeClass2 = OpenViBE_stimulation[stim_label2]
        self.codeTrain  = OpenViBE_stimulation[stim_train]  
        self.stimulations = []

    def uninitialize(self):
        pass

    def process(self):
        if not self.input[0] and not self.input[1]:
            return

        # obtain all stimulations
        stimulations = self.stimulations[:]
        while self.input[1]:
            chunk = self.input[1].pop()
            if type(chunk) == OVStimulationSet:
                for stim in chunk:                    
                    stimulations.append((stim.date,stim.identifier))
                    if stim.identifier==self.codeClass1:
                        self.currentLabel = -1
                    elif stim.identifier==self.codeClass2:
                        self.currentLabel = 1

                    if stim.identifier==self.codeTrain:
                        print('Training time...')
                        print('Nb trials:' + str(self.nbTrainData))
                        #1 - computing the correlation between each frequency band power and the class labels, for each channel
                        scorec = np.zeros((self.nbFreqs,self.num_channels))
                        for f in range(self.minFreqIdx,self.maxFreqIdx+1):
                            for c in range(self.num_channels):
                                r2 = np.corrcoef(self.spectrums[:,f,c],self.labels)
                                scorec[f,c] = r2[0,1]

                        #2 - identifying the best frequency for discrimination 
                        sumScorec = np.sum(np.abs(scorec),1)
                        fmax = sumScorec.argmax()

                        #3 - checking whether this best correlation is positive or negative
                        scorecstar = np.zeros((self.nbFreqs,self.num_channels))
                        for c in range(self.num_channels):
                            if scorec[fmax,c]>0:
                                scorecstar[:,c] = scorec[:,c]
                            else:
                                scorecstar[:,c] = -scorec[:,c]

                        #4 - computing the overall score for each frequency
                        fscore = np.sum(scorecstar,1)
                        #plt.plot(self.freq[range(self.minFreqIdx,self.maxFreqIdx+1)],fscore[range(self.minFreqIdx,self.maxFreqIdx+1)]);
                        #plt.show();
                        fmaxstar = fscore.argmax()
                        print('...done!')
                        print('Best individual frequency = ' + str(self.freq[fmaxstar]) + ' score: ' + str(fscore[fmaxstar]))
                        f0 = fmaxstar
                        f1 = fmaxstar

                        #5 - computing the min and max of the best band
                        while fscore[f0-1]>=(fscore[fmaxstar]*0.05):
                            f0 = f0-1

                        while fscore[f1+1]>=(fscore[fmaxstar]*0.05):
                            f1 = f1+1
                        print('Best band = ' + str(self.freq[f0]-0.5) + '-' + str(self.freq[f1]+0.5) + ' Hz') #we add 0.5Hz margin on each side (to avoid a pass-band with a single frequency if f0=f1)

                        #6 - saving the obtained frequency band parameters to a config file for a temporal filter
                        strToWrite = """<OpenViBE-SettingsOverride>
                                            <SettingValue>Butterworth</SettingValue>
                                            <SettingValue>Band pass</SettingValue>
                                            <SettingValue>5</SettingValue>
                                            <SettingValue>"""+str(self.freq[f0]-0.5)+"""</SettingValue>
                                            <SettingValue>"""+str(self.freq[f1]+0.5)+"""</SettingValue>
                                            <SettingValue>1</SettingValue>
                                        </OpenViBE-SettingsOverride>"""
                        file  = open(self.filename, 'w')
                        file.write(strToWrite)
                        file.close()
                        print('Config file saved!')

                        #7 - sending a stimulation to indicate that the training is complete
                        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
                        stimSet.append(OVStimulation(self.outputStimCode, self.getCurrentTime(), 0.))
                        self.output[0].append(stimSet) # Send chunk
                        

        # obtain all chunks of signals received in the first input        
        while self.input[0]:
            chunk = self.input[0].pop()

            if type(chunk) == OVSignalHeader:

                # handle header: we are sending the same information
                # so the output header should be the same
                input_header  = chunk
                self.sampling_rate = input_header.samplingRate
                self.num_channels  = input_header.dimensionSizes[0]
                self.num_samples   = input_header.dimensionSizes[1]

                #comuting an hamming window of the size of the chunks and the frequency of samples of the corresponding FFT
                self.hamWindow = np.hamming(self.num_samples)
                self.freq = np.fft.rfftfreq(self.num_samples,1./self.sampling_rate)
                self.nbFreqs = self.freq.size

                #identifying the index of the min and max frequencies to investigate
                self.minFreqIdx = (np.abs(self.freq-self.minFreq)).argmin()
                self.maxFreqIdx = (np.abs(self.freq-self.maxFreq)).argmin()
                                
            elif type(chunk) == OVSignalBuffer:

                input_signal = np.reshape(chunk, (self.num_channels, self.num_samples)) #getting the EEG chunk

                #computing the Power Spectral Density using FFT, for each channel
                psds = np.zeros((1,self.nbFreqs,self.num_channels))
                for c in range(self.num_channels):
                    psds[0,:,c] = np.log(np.abs(np.fft.rfft(input_signal[c,:]*self.hamWindow,self.num_samples))**2); #PSD based on FFT

                #storing them
                if self.nbTrainData == 0:
                    self.spectrums = psds
                else:
                    self.spectrums = np.append(self.spectrums,psds,axis=0)

                self.nbTrainData+=1
                self.labels.append(self.currentLabel)
                        

box = FrequencyBandSelectionBox()
