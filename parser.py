import math
import os, sys
import random
import inspect

if ("win" in sys.platform): sys.path.append(sys.path[0] + "\\sky");
else: sys.path.append(sys.path[0] + "/sky");

from s_sys import *
from s_str import *
from s_enum import *

opList = Enumerate("IOR XOR AND LSH RSH ADD SUB MUL DIV MOD POW FAC");
actions = Enumerate("VSHIFT OSHIFT REDUCE WAIT REPEAT");

valueTypes = Enumerate("CHAR INT FLOAT DOUBLE STRING");

stackTypes = Enumerate("OP VAL");
parseTypes = Enumerate("DYN NUM OP OBRAC CBRAC PREOP POSTOP");

opChar = "| ^ & << >> + - * / % ** !".split();
boOpList = "( [ {".split();
bcOpList = ") ] }".split();

uPreList = "-".split();
uPostList = "!".split();
fOpList = "( [ { | ^ & >> << + - * / % ** ! ) ] }".split();

paramHolder = "(,)";

digitChars = "1234567890";
fNameChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_";

funcMap = {"sin":math, "cos":math, "tan":math, "factorial":math};

def error(str, frame):
	print str,":",frame[1][3],"@",frame[1][2];

def stacks(oStack,vStack):
	print oStack,["$"]+[x.value for x in vStack if x.__class__.__name__ == "Value"];

def getFunc(name):
	try:
		module = funcMap[name];
		if (module != 0):
			return getattr(module,name);
		return globals()[name];
	except:
		return None;

class Operator:
	operatorType = None;
	def __init__(this, char):
		for c in opChar:
			if (c == char):
				this.operatorType = c;
				return;
		# Raise exception (invalid operator character)
	def eval(this, l, r):
		if (l.__class__.__name__ != "Value" and l != 0):
			error("Left-hand operator is a non-Value",inspect.getouterframes(inspect.currentframe(),2));
			return;
		if (r.__class__.__name__ != "Value" and r != 0):
			error("Right-hand operator is a non-Value",inspect.getouterframes(inspect.currentframe(),2));
			return;
		
		left = 0;
		lType = None;
		if (l != 0):
			lType = l.valueType;
			left = l.value;
			if (lType == valueTypes.INT): left = int(left);
			elif (lType == valueTypes.DOUBLE): left = float(left);
			elif (lType == valueTypes.FLOAT): left = float(left);
			elif (lType == valueTypes.CHAR): left = ord(left); # TO-DO: What if we have, char x = 5, or char x = "5", or char x = '5'?
		
		right = 0;
		rType = None;
		if (r != 0):
			rType = r.valueType;
			right = r.value;
			if (rType == valueTypes.INT): right = int(right);
			elif (rType == valueTypes.DOUBLE): right = float(right);
			elif (rType == valueTypes.FLOAT): right = float(right);
			elif (rType == valueTypes.CHAR): right = ord(right); # TO-DO: What if we have, char x = 5, or char x = "5", or char x = '5'?
		
		finalType = (rType if (lType == None or rType > lType) else lType);
		
		t = opChar.index(this.operatorType);
		
		if (t == opList.ADD):
			return Value(str(left + right),finalType);
			
		elif (t == opList.SUB):
			return Value(left - right,finalType);
			
		elif (t == opList.MUL):
			return Value(left * right,finalType);
			
		elif (t == opList.DIV):
			return Value(left / right,finalType);
			
		elif (t == opList.AND):
			return Value(left & right,valueTypes.INT);
			
		elif (t == opList.XOR):
			return Value(left ^ right,valueTypes.INT);
			
		elif (t == opList.IOR):
			return Value(left | right,valueTypes.INT);
			
		elif (t == opList.LSH):
			return Value(left << right,valueTypes.INT);
			
		elif (t == opList.RSH):
			return Value(left >> right,valueTypes.INT);
			
		elif (t == opList.MOD):
			return Value(left % right,finalType);
			
		elif (t == opList.POW):
			return Value(math.pow(left,right),valueTypes.DOUBLE);
			
		elif (t == opList.FAC):
			return Value(math.factorial(left),valueTypes.INT);
			
		return None; # Raise exception (invalid operator type)

class Value:
	valueType = None;
	value = "";
	def __init__(this, v, type):
		this.value = v;
		this.valueType = type;
	def Append(this, c):
		this.value += c;
	def AsInt(this):
		if (this.valueType in [valueTypes.INT,valueTypes.FLOAT,valueTypes.DOUBLE,valueTypes.CHAR]):
			return int(this.value);
		elif (this.valueType in [valueTypes.STRING]):
			# Check if string can be INT-ized
			return int(this.value);

def isFuncName(string):
	if (isDigit(string[0])): return False;
	for c in string:
		if (not c in fNameChars and not c in digitChars):
			return False;
	return True;

def isDynChar(c):
	return c in fNameChars;

def isDigit(string):
	for c in string:
		if (not c in digitChars): return False;
	return True;

def isPartOperator(c):
	return isOperator(c) or c in "".join(fOpList);

def isOperator(c):
	return c in fOpList or c in uPreList or c in uPostList;

def isOperatorFirst(op, cmp):
	if ("$" in [op,cmp]): return False;
	if (fOpList.index(op) >= fOpList.index(cmp)): return True;
	return False;

def evaluate(string):
	print "Parsing:",string;
	lastParsed = parseTypes.OBRAC;
	
	outputType = valueTypes.CHAR;
	
	vStack = ["$"];
	oStack = ["$"];
	inString = False;
	
	currObjType = None;
	currObjVarType = None;
	currObj = "";
	isCurrObjDone = False;
	
	i = 0;
	while (i < len(string)):
		c = string[i];
		action = [];
		repIter = False;
		passIter = False;
		eos = (i == len(string) - 1);
		j = i;
		
		# Firstly, is this a continuation of an old object, or the start of a new one?
		
		if (c in uPreList and (lastParsed == parseTypes.OP or lastParsed == parseTypes.OBRAC)):
			# Found something like a unary minus...
			if (c == "-"):
				currObj += c;
				currObjType = stackTypes.VAL;
				currObjVarType = valueTypes.INT;
				passIter = True;
				lastParsed = parseTypes.NUM;
		
		if (not passIter):
			if (isDigit(c)):
				# Found a digit.
				if (lastParsed == parseTypes.DYN or lastParsed == parseTypes.NUM):
					currObj += c;
				elif (lastParsed == parseTypes.OP or lastParsed == parseTypes.OBRAC):
					currObj = c;
					lastParsed = parseTypes.NUM;
				else:
					# Parse Error!
					pass;
				currObjVarType = (valueTypes.DOUBLE if "." in currObj else valueTypes.INT);
				currObjType = stackTypes.VAL;
				passIter = True;
			
			elif (c == "."):
				# Found a decimal point.
				if (lastParsed == parseTypes.NUM):
					currObj += ".";
				elif (lastParsed == parseTypes.OP or lastParsed == parseTypes.OBRAC):
					currObj = "0.";
					lastParsed = parseTypes.NUM;
				else:
					# Parse Error!
					pass;
				currObjType = stackTypes.VAL;
				currObjVarType = valueTypes.DOUBLE;
				passIter = True;
			
			elif (isDynChar(c)):
				# Found an A-Za-z0-9_ character
				if (lastParsed == parseTypes.DYN):
					currObj += c;
				elif (lastParsed == parseTypes.OP or lastParsed == parseTypes.OBRAC):
					currObj = c;
				else:
					# Parse Error!
					pass;
				lastParsed = parseTypes.DYN;
				currObjType = stackTypes.OP;
				passIter = True;
			
			elif (c == paramHolder[0] and lastParsed == parseTypes.DYN):
				# Found a ( after a function/var name -> function name
				currObj += c;
				currObjType = stackTypes.OP;
				isCurrObjDone = True;
				passIter = True;
				lastParsed = parseTypes.OBRAC;
			
			elif (isOperator(c) or isPartOperator(c)):
				if (lastParsed == parseTypes.NUM and currObj != ""):
					# Current object is a number; get it onto the value stack and try again
					isCurrObjDone = True;
					repIter = True;
				elif (lastParsed == parseTypes.NUM):
					if (isPartOperator(c)):
						findOp = "";
						a = 0;
						while (i+a < len(string)):
							n = string[i+a];
							a += 1;
							if (isPartOperator(findOp+n)):
								findOp += n;
							else:
								break;
						if (isOperator(findOp)):
							i += a - 2;
							currObj = findOp;
							currObjType = stackTypes.OP;
							isCurrObjDone = True;
							passIter = False;
							c = findOp;
							lastParsed = parseTypes.OP;
				else:
					# This operator is going to perform an operation instead
					if (not eos and currObj+c+string[i+1] in fOpList):
						currObj += c;
						currObjType = stackTypes.OP;
						passIter = True;
					else:
						currObj = c;
						currObjType = stackTypes.OP;
						isCurrObjDone = True;
						passIter = False;
					lastParsed = parseTypes.OP;
		
		if (isCurrObjDone or eos):
			if (currObjType == stackTypes.OP):
				oStack.append(currObj[:]);
			elif (currObjType == stackTypes.VAL):
				if (currObjVarType > outputType):
					outputType = currObjVarType;
				vStack.append(Value(currObj[:],currObjVarType));
			currObj = "";
			currObjVarType = None;
			isCurrObjDone = False;
		
		if (repIter):
			continue;
		if (not eos):
			if (oStack[-1] == "$"):
				passIter = True;
			if (passIter):
				i += 1;
				continue;
		
		# Pre-ops are not handled here.
		if (isOperator(c)):
			if (c in boOpList):
				pass;
			elif (c in bcOpList):
				reduce(oStack,vStack,1);
				lastParsed = parseTypes.CBRAC;
			elif (c in uPostList):
				reduce(oStack,vStack,1);
				lastParsed = parseTypes.NUM; # Since we evaluated something, the last value HAD to be a number.
			elif (isOperatorFirst(oStack[-2],c)):
				toReduce = oStack[:-1];
				reduce(toReduce,vStack,1);
				oStack = toReduce[:];
				lastParsed = parseTypes.NUM; # Since we evaluated something, the last value HAD to be a number.
				i = j - 1;
		
		if (eos):
			reduce(oStack,vStack);
			break;
		
		i += 1;
	
	try:
		expected = str(eval(string));
	except:
		expected = "<No calculable result>";
	x = raw_input("Result: "+str(vStack[1].value)+", expected "+expected+". Press enter to continue..\n");
	return vStack[1].value;

def reduce(oStack, vStack, levels = -1):
	r = range(len(oStack));
	r.reverse();
	l = levels;
	for i in r:
		if (l == 0): break;
		if (len(oStack) <= 1 and len(vStack) <= 2): break;
		if (oStack[i] == "$"): break;
		if (oStack[i] == "!"):
			oStack.pop();
			value = vStack.pop();
			vStack.append(Operator("!").eval(value,0));
			l -= 1;
			continue;
		if (oStack[i] == paramHolder[2]):
			j = i - 1;
			while (j >= 0):
				if (oStack[j][-1] == paramHolder[0]):
					f = getFunc(oStack[j][:-1]);
					if (f != None):
						oStack.pop(i);
						oStack.pop(j);
						vStack.append(Value(f(float(vStack.pop().AsInt())),valueTypes.DOUBLE));
						return;
				j -= 1;
		if (oStack[i] in opChar):
			result = Operator(oStack[i]).eval(vStack[-2],vStack[-1]);
			oStack.pop(i);
			vStack.pop();
			vStack.pop();
			vStack.append(result);
			l -= 1;
			continue;
		if (oStack[i] in bcOpList):
			opener = boOpList[bcOpList.index(oStack[i])];
			oStack.pop(i);
			j = i - 1;
			i -= 2;
			nOStack = [];
			nVStack = [];
			while (j >= 0):
				if (oStack[j][-1] == opener):
					nVStack.reverse();
					nVStack.insert(0,vStack.pop());
					oStack.pop(j);
					nOStack.reverse();
					nVStack = ["$"]+nVStack;
					nOStack = ["$"]+nOStack;
					reduce(nOStack,nVStack);
					vStack.append(nVStack[1]);
					return;
				else:
					nOStack.append(oStack.pop(j));
					nVStack.append(vStack.pop());
					i -= 1;
				j -= 1;
			l -= 1;
			continue;
		l -= 1;

print evaluate("5120/2**9"); # 10.0
print evaluate("sin(2)+factorial(4)+cos(8)"),"\n"; # 24.763797393017068169527178484081
print evaluate("32<<3"),"\n"; # 256
print evaluate("(7<<1+32>>4)"),"\n"; # 3758096384 == ((7<<(1+32))>>4)
print evaluate("(7>>1+32<<4)"),"\n"; # 0 == (7<<((1+32)>>4))
print evaluate("17+35/7-18/3"),"\n"; # 16
print evaluate("17+(35/7)-18/3"),"\n"; # 16
print evaluate("(5)*((5)/(3))"),"\n"; # 5
print evaluate("(5)*((5.0)/(3))"),"\n"; # 8.33...
print evaluate("7+2*1&4+1"),"\n"; # 1
print evaluate("6*.5"),"\n"; # 3
print evaluate("6!+5"),"\n"; # 725
print evaluate("6!^120"),"\n"; # 680
print evaluate("-1"),"\n"; # -1
print evaluate("-1+5"),"\n"; # 4
print evaluate("-1+-5"),"\n"; # -6
print evaluate("(-7+6%4*2)"),"\n"; # -3
print evaluate("(5120/512+7&2-7|2+7^2)"),"\n"; # 27
print evaluate("(7<<1+32>>4)"),"\n"; # 3758096384
print evaluate("(-7+6%4*2)-(5120/512+7&2-7|2+7^2)+(7<<1+32>>4)"),"\n"; # 3758096354
