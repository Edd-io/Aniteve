import os
import fcntl
import atexit

class WorkerLock:
	def __init__(self, lock_name):
		self.lock_name = lock_name
		self.lock_file_path = f'/tmp/aniteve_{lock_name}.lock'
		self.lock_file = None
		self.is_locked = False
	
	def acquire(self):
		try:
			self.lock_file = open(self.lock_file_path, 'w')
			fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
			self.is_locked = True
			self.lock_file.write(str(os.getpid()))
			self.lock_file.flush()
			atexit.register(self.release)
			return True
		except (IOError, OSError) as e:
			if self.lock_file:
				self.lock_file.close()
				self.lock_file = None
			return False
	
	def release(self):
		if self.is_locked and self.lock_file:
			try:
				fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
				self.lock_file.close()
				if os.path.exists(self.lock_file_path):
					os.remove(self.lock_file_path)
			except Exception as e:
				pass
			finally:
				self.is_locked = False
				self.lock_file = None
	
	def __enter__(self):
		return self.acquire()
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.release()
		return False
