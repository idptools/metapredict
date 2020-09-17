"""
Backend for graphing predicted disorder values in meta.py.
"""


#code for graphing IDRs.
#Import stuff
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from metapredict.backend import meta_predict_disorder
from metapredict.backend.meta_predict_disorder import meta_predict as predict

def graph(sequence, name = " ", line_color = "blue", DPI = 150, save_fig = False, output_file = "./predicted_disorder.png"):
	"""
	Function for graphing predicted disorder. By default, this function will show a graph.
	However, if saveFig = True, then it will save the figure (by default) to the location
	where the script is (which isn't ideal). However, you can specify outputFile as the
	file path followed by the name of the saved file with the proper extension (.png by default).
	This is the backend for the meta.py graphing functions.

	Arguments
	---------
	sequence - Input amino acid sequence (as string) to be predicted.

    name (optional) - setting the value of name will change the title of the
    graph. By default, the title is "Predicted Protein Disorder", so if you
    for example set name = "- PAB1", the title on the graph will be "Predicted
    Protein Disorder - PAB1". 

    line_color (optional) - set the color of the predicted disorder values line. Default is blue.

    DPI (optional) - default value is 150. Increasing this value will increase
    the resolution of the output graph. Decreasing this value will decrease
    the resolution.
	
	save_fig (optional) - by default will not save the figure and will instead show it immediately.
	Set save_fig = True in order to save the figure.
	***important***
	If you set save_fig = True, you must specify an output file!

	output_file - the path to where the output graph should be saved followed by the file name. 
    For example, on MacOS:
    output_file="Users/thisUser/Desktop/folder_of_cool_graphs/my_cool_protein.png"

    This code is meant to be backend code for meta.py.
	"""
	#set yValues equal to the predicted disorder from the sequence (normalized)
	yValues = predict(sequence)
	#set title of figure to Predicted Protein Disorder followed by the name if given
	Title = "Predicted Consensus Disorder {}".format(name)
	#if a name is set, the figure will hold that name as the identifier
	fig = plt.figure(num = name, figsize = [8, 3], dpi = DPI, edgecolor = 'black')
	axes = fig.add_axes([0.15, 0.15, 0.75, 0.75])
	axes.set_title(Title)
	axes.set_xlabel("Position Across Protein Sequence")
	axes.set_ylabel("Consensus Disorder Score")
	#make x values for each residue with predicted disorder
	xValues = np.arange(0, len(yValues))
	#graph the disorder values of each residue at each point along the x-axis
	axes.plot(xValues, yValues, color = line_color, linewidth = '1.6')
	#set x limit as the number of residues
	axes.set_xlim(0, len(xValues))
	#set y limit as 0-1 since the predictor data is normalized from 0 to 1.
	axes.set_ylim(-0.003, 1.003)

	#graph "disorder cutoff line at 0.5"
	disorderValues = []
	for i in range(0, len(yValues)):
		disorderValues.append(0.5)
	axes.plot(xValues, disorderValues, color = "black", linewidth = "1.25")
	#add dashed lines at 0.2 intervals
	cutoffLines = [0.2, 0.4, 0.6, 0.8]
	for i in cutoffLines:
		tempList = []
		for j in range(0, len(yValues)):
			tempList.append(i)
		axes.plot(xValues, tempList, color = "black", linestyle = "dashed", linewidth = "0.75")
	if save_fig == False:
		plt.show()
	else:
		plt.savefig(fname = output_file, dpi = DPI)
		plt.close()
