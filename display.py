# pyTools.display

from progressbar import ProgressBar, Percentage, Bar, Timer, UnknownLength
from tabulate import tabulate

__all__ = ['show', 'transpose', 'defaultPB']

def defaultPB(size):
	return ProgressBar(widgets=[Percentage(), Bar(), Timer()], max_value=size)

def show(data, limit = False, truncate = False, toPrint = True):
	if limit == False:
		data = list(data)
	else:
		limited = []
		i = 0
		for d in data:
			limited.append(d)
			i += 1
			if i >= limit:
				break
		data = limited

	if len(data) == 0:
		print("Nothing returns")
		return None

	keys = list( data[0].keys() )
	if "Key" in keys:
		keys = [k for k in keys if k != "Key"]
		keys.append("Key")
		keys.reverse()

	p = tabulate([ [ str(d[k])[:20]+"..." if truncate==True and len(str(d[k]))>20 else d[k] for k in keys ] for d in data ], keys)
	if toPrint == True:
		print( p )
	# return p

def transpose(data):
	trans = {}
	for d in data:
		for k in d:
			if not(k in trans):
				trans[k] = []
			trans[k].append( d[k] )
	return iter([ { **{"Key": k}, **dict(zip(range(len(trans[k])), trans[k])) } for k in trans ])
