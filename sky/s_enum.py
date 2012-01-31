class Enumerate(object):
	legend = "";
	def __init__(this, names):
		this.legend = names;
		for number, name in enumerate(names.split()):
			setattr(this, name, number);
	def get(this, index):
		return this.legend.split()[index];
