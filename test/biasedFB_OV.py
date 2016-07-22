# we use numpy to compute the mean of an array of values
import numpy
from math import *

# let's define a new box class that inherits from OVBox
class MyOVBox(OVBox):   
	def __init__(self):
		OVBox.__init__(self)
		self.instruction = 0.0
		self.baseline = 'other'
		self.counter=0
		self.stimulation_header = None
		self.matrix_header = None

	def process(self):
		
		#browing stimulations
		for stim_index in range(len(self.input[0])):

			if(type(self.input[0][stim_index]) == OVStimulationHeader):
				self.stimulation_header = self.input[0].pop()

			#if stimulation are left/right instruction set a corresponding flag
			elif(type(self.input[0][stim_index]) == OVStimulationSet):
				stim = self.input[0].pop()
				while(len(stim)>0):
					st = stim.pop()
					if( (st.identifier==769) or (st.identifier==770)):
						self.instruction = st.identifier - 769.5
					elif(st.identifier==32775):
						self.baseline = 'start' 
					elif(st.identifier==32776):
						self.baseline = 'stop'
					else :
						self.baseline = 'other'
					
		#browsing the input signal to be modified according to the current instruction(left/right)
		for chunk_index in range(len(self.input[1])):
		
			#passing on the header to the output
			if(type(self.input[1][chunk_index]) == OVStreamedMatrixHeader):
				self.matrix_header = self.input[1].pop()
				
			#biasing the input signal to output it
			elif(type(self.input[1][chunk_index]) == OVStreamedMatrixBuffer):
				inputChunk = self.input[1].pop()
				numpyBuffer = numpy.matrix(inputChunk).reshape(tuple(self.matrix_header.dimensionSizes))
				if self.baseline == 'start':
					numpyBuffer = [-0.5]
				elif self.baseline == 'stop':
					numpyBuffer = [0.5]
				elif self.baseline == 'other':
					numpyBuffer = numpyBuffer + copysign(0.2, self.instruction)
					numpyBuffer = [copysign(ceil(abs(numpyBuffer)*10), numpyBuffer)/10]
				outputChunk = OVStreamedMatrixBuffer(inputChunk.startTime, inputChunk.endTime, numpyBuffer)
				outputChunkHeader = OVStreamedMatrixHeader(self.matrix_header.startTime,self.matrix_header.endTime,self.matrix_header.dimensionSizes,'biasedOutput');
				self.output[0].append(outputChunkHeader)
				self.output[0].append(outputChunk)
				#self.output[0].append(inputChunk)
				#print('input:',inputChunk)
				#print('output:',outputChunk)

			#ending the output signal if needed
			elif(type(self.input[1][chunk_index]) == OVStreamedMatrixEnd):
				#print('streamedMatrixEnd')
				self.output[0].append(self.input[1].pop())

box = MyOVBox()
