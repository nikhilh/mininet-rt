"Command class - run a command inside a node"

import os
import signal
from subprocess import Popen, PIPE
import select

class Command:

  def __init__(self, c):
    if type(c) == type(''):
      c = c.split(' ')
    self.cmd = c
    self.p = Popen(c, stdout=PIPE, stdin=PIPE)

  def readFull(self):
    # warning, will BLOCK until we read all output
    #return self.p.communicate()[0]
    # communicate uses select() that cannot deal with more
    # than 1024 open file descriptors per process.
    # we use epoll.
    ret = ''
    epoll = select.epoll()
    epoll.register(self.p.stdout.fileno(), select.EPOLLIN)
    done = False
    try:
        while not done:
            events = epoll.poll(1)
            for fileno, event in events:
                if fileno == self.p.stdout.fileno():
                    if event & select.EPOLLIN:
                        while True:
                            data = self.p.stdout.read(1024)
                            if len(data) == 0:
                                done = True
                                break
                            ret += data
            continue # while loop
    finally:
        epoll.unregister(self.p.stdout.fileno())
        epoll.close()
    return ret

  def readN(self, n):
    toread = n
    data = ''
    while toread:
      data = self.p.stdout.read(toread)
      toread -= len(data)
    return data

  def readLine(self):
    return self.p.stdout.readline()

  def write(self, data):
    """
      There might be cases where you might want to 
      write() data into the program. e.g., you've 
      spawned a shell and you write a command to it,
      it will be interpreted by the shell
    """
    self.p.stdin.write(data)

  def writeLine(self, data):
    self.write(data + '\n')

  def poll(self):
    """ 
      poll checks if our command has terminated.
      if yes, then returns the return code
      else dunno what it does; python doc doesn't tell.
      but it's non blocking
    """
    return self.p.poll()

  def wait(self):
    return self.p.wait()

  def kill(self):
    return os.kill(-self.p.pid, signal.SIGKILL)

  def signal(self, signal):
    return self.p.send_signal(signal)

  def waitOutput(self):
    return self.readFull()

