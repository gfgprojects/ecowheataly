#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A library for the C-index calculation
"""

import numpy as np
from matplotlib import pyplot as plt

# ---------------------------------------------------
# setting colors for the boxplot
colors = ['tab:blue', 'orange', 'darkgrey']
mark = dict(marker='.', markersize=6)


def monotonic(x):
	"""

	Mmonotonic  identifies the components under a monotonic
	increase of the computed Distance
	x = monodimensional array

	"""
	components = [0]
	for i in range(1, len(x)):
		if (x[i] >= x[i - 1]) == True:
			components.append(i)
		else:
			break
	return components


def Cindex(I, features, pos_flag, neg_flag, plot, verbose):
	"""
Cindex computes the composite index from a set of indipendent variables
that maximize the euclidean distance between two subset of data identified
by an indicator variables (or condictional variable)


		Parameters
		----------
		I : numpy array (floats) of shape (N x M) where N are the number of observation and M the number of variables;
			Input variables

		features : numpy array (strings) of shape (M,) encoding the name of the variables; i.e., variables' short name

		pos_flag : numpy array (integers) of shape (p,);
			the ID rows of I under the negative  condiction

		neg_flag : numpy array (integers) of shape (n,);
				the ID rows of I under the negative  condiction

		plot : boolean (True or False)
			set plot=True for producing the figures

		verbose : boolean (True or False)
			set verbose=True for printing the results

		Returns
		-------
		DD : list of size M; each element is a numpy array of floats of shape (M,)
			DD holds the distances computed by the algorithm for a given starting variables computed by the addiction or subtraction of remaining variables;

		Var : list of size M; each element is a numpy array of strings of shape (M,)
			Var holds the variables' label linked to the DD outputs

		Operator : same type of Var;
			Operator specify wheather each variables has been substracted or summed by the algortihm:
				'+' == summed
				'-' == subtracted

		CC : list of size M; each element is a list of integers of variable length
			CC tracks back the first componentes underlying a monotonic increase of the distance linked to the related starting variable
	"""
	# allocationg the outputs:
	DD = []
	Var = []
	Operator = []
	CC = []
	cnt = 0
	# the results depend on the starting variable;
	# the algorithm tests each variable as "starting varibale" (ii-loop)
	for ii in range(np.shape(I)[1]):  # prima vedere tutti e poi in a mettere i migliori loop con "for in in a"
		# select a firs variable from I (x)
		# n=ii
		x = I[:, ii]

		# make a copy of I yet without the selected variable (Inew)
		Inew = np.array(I, copy=True)
		Inew = np.delete(Inew, ii, axis=1)
		# make a copy of "features" yet without the name of the selected variable (featnew)
		featnew = np.array(features, copy=True)
		featnew = np.delete(featnew, ii)
		# start to allocate the name of the selected variable in the "var" list
		var = []
		var.append(features[ii])
		# estimate (and put in proper list D) the distance for the selected variable under condictional flag
		# Note: the distance is computed as a ratio betwen a numerator (num) and denominator (den)
		num = (np.mean(x[pos_flag]) - np.mean(x[neg_flag])) ** 2
		den = np.std(x[pos_flag]) ** 2 + np.std(x[neg_flag]) ** 2
		D = []
		D.append(num / den)

		# stress direction and operator: specular information that are always computed for check
		direction = []  # stress direction
		operator = []  # operator: "+" when the variable is summed ; "-" if subtracted
		operator.append('+')  # the first variables holds its original sign
		# the stress direction of the first variable determines the order of the boxplot diagram:
		# blue box on the righr-side of the panel if the first variable has a positive stress direction; (+)
		# blue box on the left-side of the panel  if the first variable has a negative stress direction (-)
		if np.mean(x[neg_flag]) > np.mean(x[pos_flag]):
			direction.append('+')
		else:
			direction.append('-')

		if verbose == True:
			print("ii-loop = %s: initial variable = %s, direction = %s" % (str(ii), features[ii], str(direction[0])))

		# ---------------------------------------------------------------------------
		# Now let's see which variables increased the distance under the condition...
		while True:  # the loop goes on until each variabele is tested and selected
			# I will try both addition(+) and substraction(-). The best choice (i.e., '+' or '-') is stored in operatore_d
			operator_d = []
			d = []
			direction_d = []
			# at each "i" loop the script select a remaining variable and test its addition/substraction
			for i in range(np.shape(Inew)[1]):
				# select a variable among those remaning
				x2 = Inew[:, i]
				# if added the result is D1
				vec1 = x + x2  # added
				num1 = (np.mean(vec1[pos_flag]) - np.mean(vec1[neg_flag])) ** 2
				den1 = np.std(vec1[pos_flag]) ** 2 + np.std(vec1[neg_flag]) ** 2
				D1 = np.round(num1 / den1, 4)
				# when substracted the result is D2
				vec2 = x - x2  # substracted
				num2 = (np.mean(vec2[pos_flag]) - np.mean(vec2[neg_flag])) ** 2
				den2 = np.std(vec2[pos_flag]) ** 2 + np.std(vec2[neg_flag]) ** 2
				D2 = np.round(num2 / den2, 4)

				# Now let's see wether D1>D2 or vice versa. The largest results is selected and
				# stored in "d". The best operator is stored in "operator_d"
				if D1 > D2:
					d.append(D1)
					operator_d.append('+')
					if direction[0] == '+':
						direction_d.append('+')
					else:
						direction_d.append('-')
				elif D2 > D1:
					d.append(D2)
					operator_d.append('-')
					if direction[0] == '-':
						direction_d.append('+')
					else:
						direction_d.append('-')

			d = np.array(d)
			# at the end of each i-loop I will select the best variable (that mostly increase the distance).
			# Such variable is store in "var" and related result in "D" before being deleted from Inew
			try:
				D.append(np.max(d))
				var.append(featnew[np.argmax(d)])
				operator.append(operator_d[np.argmax(d)])
				direction.append(direction_d[np.argmax(d)])

				# removing features
				if operator[-1] == '+':
					x = np.round(x + Inew[:, np.argmax(d)], 4)
				elif operator[-1] == '-':
					x = np.round(x - Inew[:, np.argmax(d)], 4)

				Inew = np.delete(Inew, np.argmax(d), axis=1)
				featnew = np.delete(featnew, np.argmax(d))

			except ValueError:
				break

		var = np.array(var)
		D = np.round(np.array(D), 4)
		operator = np.array(operator)
		components = monotonic(D)
		if verbose == True:
			print('selected components for the ii-loop defining the composite index:')
			for j in range(len(components)):
				print('    %s %s %s' % (direction[components[j]], var[components[j]], np.round(D[components[j]], 2)))
			print('Distance reached: %s' % (np.round(D[components[-1]], 2)))
			# LET'S PLOT THE RESULTS
			print('plotting the result in fig.' + str(ii + 1))
			print('*********************************')

		# PLOTTING

		if plot == True:
			cnt = cnt + 1
			fig, (ax1, ax2) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [2, 1]}, num=cnt)
			# fig.suptitle('Horizontally stacked subplots')
			ax1.plot(np.arange(len(D)), D, '-o', color='grey')
			ax1.plot(np.arange(0, len(components)), D[0:len(components)], '-o', color='black')
			ax1.set_xticks(np.arange(len(D)))
			labels = [direction[j] + var[j] for j in range(len(var))]
			ax1.set_xticklabels(labels, rotation=90, fontsize=14)
			ax1.set_ylabel('D', fontsize=14)
			ax1.grid()
			# ------ BOXPLOT----------

			# --------------PARTE IN COMUNE ------------------------------
			# COMPONENTS added to the initial one:
			varid = [np.where(features == var[j])[0][0] for j in components[1::]]
			A = np.array(I[:, ii], copy=True)  # initial variables plus...
			for j in range(len(varid)):
				if operator[j + 1] == '+':
					A = np.round(A + I[:, varid[j]], 4)
				elif operator[j + 1] == '-':
					A = np.round(A - I[:, varid[j]], 4)
			# skip the frst sigh of perator as it refers to the initial variable
			# exec( 'A = A '+operator[i+1]+' I[:,varid['+str(i)+']]')

			a = [A[neg_flag], A[pos_flag], A]  # low,high and all data
			bp = ax2.boxplot(a, patch_artist=True,
			                 notch='True', vert=False, flierprops=mark)

			for patch, color in zip(bp['boxes'], colors):
				patch.set_facecolor(color)
			for median in bp['medians']:
				median.set(color='brown', linewidth=3)
			ax2.set_yticklabels([' ', ' ', ' '])
			ax2.set_xlabel('composite z-score', fontsize=14)
			ax2.set_xlim([-15, 15])
			plt.tight_layout()
			plt.show()

		DD.append(np.array(D))
		Var.append(np.array(var))
		Operator.append(np.array(direction))
		CC.append(monotonic(np.array(D)))

	return (DD, CC, Var, Operator)