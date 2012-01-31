import math
import os, sys
import random

class String:
	@staticmethod
	def AsArray(str, seps = " "):
		arr = list();
		tstr = "";
		for c in str:
			if (seps == ""):
				arr.append(c);
			elif (c in seps):
				arr.append(tstr);
				tstr = "";
			else:
				tstr += c;
		if (seps != ""): arr.append(tstr);
		return arr;
	@staticmethod
	def FromArray(arr, seps = " "):
		tstr = "";
		for c in arr:
			tstr += c + seps;
		tstr = tstr[0:len(tstr) - len(seps)];
		return tstr;
	@staticmethod
	def Remove(str, removes, num = -1):
		tstr = "";
		found = 0;
		for c in str:
			if (not c in removes):
				tstr += c;
				found += 1;
				if (found >= num and num > 0):
					break;
		return tstr;
