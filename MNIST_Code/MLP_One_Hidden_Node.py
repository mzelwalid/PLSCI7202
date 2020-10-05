import numpy as np
import time

start_time = time.time()

epochs = 30
lRate = 0.1
momentum = 0.1

trainDataFileName = 'mnist_train_minimized_subset.txt'
trainLabelFileName = 'mnist_train_label_minimized_subset.txt'

testDataFileName = 'mnist_test_data_subset_minimized.txt'
testLabelFielName = 'mnist_test_data_subset_label_minimized.txt'

class HiddenNode:
	weights = np.array([0])
	weightsOld = np.array([0.0])
	bias = 0.0
	net = 0.0
	out = 0.0
	d = 0.0
	def __init__(self, weights, bias):
		self.weights = weights
		self.weightsOld = weights
		self.bias = bias

class OutputNode:
	weights = np.array([0.0])
	weightsOld = np.array([0.0])
	bias = 0.0
	net = 0.0
	out = 0.0
	error = 0.0
	d = 0.0
	def __init__(self, weights, bias):
		self.weights = weights
		self.weightsOld = weights
		self.bias = bias

#functions for forward pass
def netCalcInput(node, inputArray):
	net = 0
	i = 0
	for w in node.weights:
		net += w * inputArray[i]
		i += 1
	net += node.bias
	return net

def netCalc(node, prevLayer):
	net = 0
	i = 0
	for w in node.weights:
		net += w * prevLayer.out
		i += 1
	net += node.bias
	return net

def tanh(i):
        return np.tanh(i)
        #return ((np.e**(i)-np.e**(-i))/(np.e**(i)+np.e**(-i)))

def sigmoid(i):
    return 1/(1 + np.exp(-i))

def sumError(nodeOut, target):
	var = target - nodeOut
	var *= var
	var /= 2
	return var

#Functions for back prop
def outputUpdate(out, target):
        var = -(target - out)
        return (var * (out * (1 - out)))
	

def layerUpdate(prevLayer, net, i):
        netD = 0.0
        for node in prevLayer:
            netD += node.d * (node.weightsOld[i])
        return (netD * (1 - (tanh(net) * tanh(net) )))
	

#--------------read in training data-----------------

with open(trainDataFileName) as inputD:
    linesD=inputD.readlines()

data = []
for line in linesD:
    data.append(np.fromstring(line, dtype=float, sep='\t'))

with open(trainLabelFileName) as inputL:
    linesL=inputL.readlines()

labels = []
for lines in linesL:
    temp = np.zeros(10)
    temp[int(lines)] = 1
    labels.append(temp)

merged_data = [(data[i], labels[i]) for i in range(0, len(data))]

#-----Read in test set----------
with open(testDataFileName) as inputD:
    linesD=inputD.readlines()

test = []
for line in linesD:
    test.append(np.fromstring(line, dtype=float, sep='\t'))

with open(testLabelFielName) as inputL:
    linesL=inputL.readlines()

testlabels = []
for lines in linesL:
    temp = np.zeros(10)
    temp[int(lines)] = 1
    testlabels.append(temp)
	
merged_test = [(test[i], testlabels[i]) for i in range(0, len(test))]



#------Generate nodes for each layer---------
layerOne = HiddenNode(np.random.uniform(-0.2,0.2,196), np.random.ranf(1))

layerOut = []
for x in range(10):
    layerOut.append(OutputNode(np.random.uniform(-0.2,0.2,100), np.random.ranf(1)))

#-----Pre declerations-----
outputs = []
outputHold = np.zeros(10)
f = open("weights" + "_epochs" + str(epochs) + "_trainSize" + str(len(data)) + "_testSize" + str(len(test)) +".txt", "w")
errorOut = open("sse_by_epoch" + "_epochs" + str(epochs) + "_trainSize" + str(len(data)) + "_testSize" + str(len(test)) + ".txt", "w")
run = 0

for x in range(epochs):
	sse = 0
	for i in merged_data:
		f.write("\n\nPass: " + str(run + 1) + "\n")

		#forward pass
		data = i[0]
		truth = i[1]
		
		
		layerOne.net = netCalcInput(layerOne, data)
		layerOne.out = tanh(layerOne.net) 
		layerOne.weightsOld = np.array(layerOne.weights)
		
		j = 0
		for node in layerOut:
			node.net = netCalc(node, layerOne)
			node.out = sigmoid(node.net)
			node.weightsOld = np.array(node.weights)
			outputHold[j] = node.out
			sse += sumError(node.out, truth[j])
			j += 1
			
		outputs.append(np.array(outputHold))
		
		#Back prop

		#Output Layer Update

		j = 0
		for node in layerOut:
				f.write("\n")
				i = 0
				node.d = outputUpdate(node.out, truth[j])
				for w in node.weights:
					node.weights[i] = w - (lRate * layerOne.out * node.d + (momentum * (node.weightsOld[i] - w)))
					i += 1
				node.bias = node.bias - lRate * node.d
				j += 1
		
		
		#Layer One Update
		j = 0
		i = 0
		layerOne.d = layerUpdate(layerOut, layerOne.net, j)
		for w in node.weights:
						layerOne.weights[i] = w - (lRate * data[i] * layerOne.d + (momentum * (layerOne.weightsOld[i] - w)))
						i += 1
		layerOne.bias = layerOne.bias - lRate * layerOne.d
		j += 1
		run += 1
	errorOut.write(str(x) + "\t" + str(sse) + "\n")
	
f.close()



#-----Test trained MLP--------

print("Test set running")
sse = 0
outputHold = np.zeros(10)

f = open("testSetCalls" + "_epochs" + str(epochs) + "_trainSize" + str(len(data)) + "_testSize" + str(len(test)) +".txt", "w")
for i in merged_test:
		#forward pass
		data = i[0]
		truth = i[1]
		
		
		layerOne.net = netCalcInput(layerOne, data)
		layerOne.out = tanh(layerOne.net) 
		
		j = 0
		for node in layerOut:
			node.net = netCalc(node, layerOne)
			node.out = sigmoid(node.net)
			outputHold[j] = node.out
			sse += sumError(node.out, truth[j])
			j += 1
		lrgst = 0
		j = 0
		for val in outputHold:
			if val > outputHold[lrgst]:
				lrgst = j
			if truth[j] == 1:
				f.write(str(j) + "\t")
			j += 1
		f.write(str(lrgst) + "\n")
f.write("SSE: " + str(sse))
f.close()

print("--- %s seconds ---" % (time.time() - start_time))
