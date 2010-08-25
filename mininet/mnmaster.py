'''The mininet master script'''

import sys
from time import sleep
import xmlrpclib
from xmlrpclib import ServerProxy, Binary
from cPickle import dumps, loads
from mininet.topo import Topo, SingleSwitchTopo

serverIP = '127.0.0.1'
serverPort = 8000
server = None

class MininetMasterService:
    '''A mininet proxy to the slaves'''

    def mininetStart(self, topo, cparam):
        '''Start mininet with the given topo and ctrlr params as args'''
        global server, serverIP, serverPort
        t = Topo()
        t.g = topo.g
        t.node_info = topo.node_info
        t.edge_info = topo.edge_info
        t.ports = topo.ports
        t.id_gen = topo.id_gen
        server = ServerProxy('http://%s:%d/' % (serverIP, serverPort), allow_none=True)
        try:
            server.mininetStart(Binary(dumps(t)), Binary(dumps(cparam)))
        except xmlrpclib.Fault as e:
            print e
            exit(1)

    def mininetStop(self):
        server.mininetStop()

    def mininetGetHosts(self):
        phosts = server.mininetGetHosts()
        hosts = loads(phosts.data)
        return hosts

    def mininetGetSwitches(self):
        pswitches = server.mininetGetSwitches()
        switches = loads(pswitches.data)
        return switches

    def getHostIP(self, hostName, intf=None):
        return server.getHostIP(hostName, intf)

    def getCmd(self, hostName, cmd):
        return server.getCmd(cmd)

    def cmdSend(self, hostName, cmd):
        return server.cmdSend(hostName, cmd)

    def cmdReadLine(self, hostName, handle):
        return server.cmdReadLine(handle)

    def cmdWaitOutput(self, hostName, handle):
        return server.cmdWaitOutput(handle)

    def cmdKill(self, hostName, handle):
        return server.cmdKill(handle)

    def cmdWait(self, hostName, handle):
        return server.cmdWait(handle)


if __name__ == '__main__':
    size = 2
    if(len(sys.argv) > 1):
        serverIP = sys.argv[1]
    if(len(sys.argv) > 2):
        try:
            serverPort = int(sys.argv[2])
        except ValueError:
            print 'Could not convert arg %s to int - using default value' % sys.argv[2]

    #try starting the network
    cparam = ('127.0.0.1', 6633)
    try:
        server.mininetStart(Binary(dumps(SingleSwitchTopo(k=size))), Binary(dumps(cparam)))
    except xmlrpclib.Fault as e:
        print e
        exit(1)
    sleep(2)
    print 'Started the network...'
    ping = server.getCmd('ping')
    phosts = server.mininetGetHosts()
    hosts = loads(phosts.data)
    cmd = '%s -c 3 10.0.0.2' % ping
    c = server.cmdSend(hosts[0], cmd)
    print server.cmdWaitOutput(c)
    server.mininetStop()
