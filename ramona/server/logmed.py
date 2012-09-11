import collections, io, os

###

class log_mediator(object):
	'''
	This object serves as mediator between program and its log files.

	It provides following functionality:
		- log rotation (TODO)
		- tail buffer (TODO)
		- seek for patterns in log stream and eventually trigger error mail
	'''

	maxtailbuflen = 64*1024 # 64Kb is max len. of tail buffer

	def __init__(self, fname):
		'''
		@param fname: name of connected log file, can be None if no log is connected
		'''
		self.fname = fname
		self.outf = None

		self.tailbuf = collections.deque()
		self.tailbuflen = 0

		# Read last content of the file into tail buffer
		if self.fname is not None and os.path.isfile(self.fname):
			with io.open(self.fname, 'r') as logf:
				if logf.seekable(): 
					logf.seek(0, io.SEEK_END)
					d = max(logf.tell() - self.maxtailbuflen, 0)
					logf.seek(d, io.SEEK_SET) # Seek to tail start position (end of file - maxtailbuflen)
					while True: # Read line by line into tail buffer
						data = logf.readline(4096)
						datalen = len(data)
						if datalen == 0: break
						self.__add_to_tailbuf(data)


	def open(self):
		if self.outf is None and self.fname is not None:
			self.outf = open(self.fname,'a')
			

	def close(self):
		if self.outf is not None:
			self.outf.close()
			self.outf = None


	def write(self, data):
		if self.outf is not None:
			self.outf.write(data)
			self.outf.flush() #TODO: Maybe something more clever here can be better (check logging.StreamHandler)

		self.__add_to_tailbuf(data)


	def __add_to_tailbuf(self, data):
		# Add data to tail buffer
		datalen = len(data)
		self.tailbuf.append((data, datalen))
		self.tailbuflen += datalen

		# Clean tail buffer - data that exceeds max. length
		while self.tailbuflen > self.maxtailbuflen:
			try:
				_, odatalen = self.tailbuf.popleft()
			except IndexError:
				self.tailbuflen = 0
				break

			self.tailbuflen -= odatalen


	def tail(self):
		d = collections.deque()
		dlen = 0
		for data, datalen in reversed(self.tailbuf):
			dlen += datalen
			if dlen >= 0x7fff: break #Protect maximum IPC data len
			d.appendleft(data)

		return "".join(d)

# # Following code is just example
#
# Init:
# Log searching (just example)
#self.kmp = kmp_search('error')
#
# Use:
# if sourceid == 1:
# 	i = self.kmp.search(data)
# 	if i >= 0:
# 		# Pattern detected in the data
# 		pass
