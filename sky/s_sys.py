import math
import os, sys
import random

class System:
	@staticmethod
	def ExecPath():
		if ("win" in sys.platform): app = "\\";
		else: app = "/";
		return sys.path[0] + app;
