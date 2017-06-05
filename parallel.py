import multiprocessing as mp
import json, pickle, os, tempfile, time

from functools import partial, reduce
from itertools import chain
from collections import Iterable

from threading import Thread
from random import random
from copy import deepcopy

from .display import defaultPB



__all__ = ['isIter', 'parmap', 'parfilter', 'map', 'partial', 'reduce']


def isIter(it): return isinstance(it, Iterable)


_bt_map_ = map
def map(func, l, bar=False):
	if bar == True:
		try:
			return defaultPB(len(l))( _bt_map_(func, l) )
		except:
			print("no length information provided")
	return _bt_map_(func, l)

# parmap

def spawn(f, qin, qout, qcount, temp, i):
	tempfnbase = None
	if temp != False:
		tempfnbase = os.path.join( temp, str( int(random()*1000000) ) + "-" + str(i) + "-" )

	c = 0
	f = pickle.loads(f)

	while True:
		x = qin.get()
		if x == None:
			# break
			break
		if tempfnbase != None:
			with open( os.path.join(tempfnbase, str(c)), "wb" ) as fw:
				pickle.dump( f(x), fw )
				fw.close()
			qout.put_nowait( os.path.join(tempfnbase, str(c)) )
		else:
			qout.put( f(x) )
		# qcount.put_nowait(1)
		c += 1

def parmap(target, inputs, bar=True, temp=False, tasks=mp.cpu_count()):

	inputs = list(inputs)
	pbar = defaultPB(len(inputs)).start()
	pbar.update(0)
	isfinished = False

	if temp == "default":
		temp = tempfile.mkdtemp()

	try:
		qin = mp.Queue(1)
		qout = mp.JoinableQueue()
		qcount = mp.Queue()
		try:
			proc = [ mp.Process(target=spawn, args=( pickle.dumps(target) , qin, qout, qcount, temp, i)) for i in range(tasks) ]
		except (pickle.PicklingError, AttributeError):
			import cloudpickle # use more powerful pickler
			proc = [ mp.Process(target=spawn, args=( cloudpickle.dumps(target) , qin, qout, qcount, temp, i)) for i in range(tasks) ]
		except Exception as e:
			raise e

		def updating():
			counter = 0
			while not( isfinished or counter == len(inputs) ):
				if not(qcount.empty()):
					qcount.get()
					counter += 1
				try:
					pbar.update( qout.qsize() )
				except NotImplementedError:
					pbar.update(counter)
				time.sleep(0.5)
		Thread(target=updating).start()
		for p in proc:
			p.daemon = True
			p.start()

		[ qin.put(x) for x in inputs ]
		[ qin.put(None) for _ in range(tasks) ]
		if temp == False:
			isfinished = True
			pbar.finish()
			results = [ qout.get() for _ in range(len(inputs)) ]
			qout.close()
			def ret():
				while len(results) > 0:
					yield results.pop()
		else:
			fns = []
			for i in range(len(inputs)):
				fns.append( qout.get() )
			qout.close()
			[ p.join() for p in proc ]
			def ret():
				for fn in fns:
					yield pickle.load( open(fn, "rb") )
					os.remove( fn )


	except KeyboardInterrupt:
		print("[Keyboard Interrupt]")
	except Exception as e:
		raise e
	finally:
		qin.close()
		[ p.terminate() for p in proc ]
		[ p.join() for p in proc ]

	pbar.finish()

	isfinished = True

	return ret()


def parfilter(ld, it, bar=True, tasks=mp.cpu_count()):
	des = [ d[1] for d in sorted( parmap( lambda x: (x[0], ld(x[1])) , enumerate(it), tasks=tasks, bar=bar), key=lambda x:x[0]) ]

	return (c for c, keep in zip(it, des) if keep)
	