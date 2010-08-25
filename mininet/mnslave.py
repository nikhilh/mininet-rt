'''A simple xml rpc server that runs on each physical node,
get commands from the master and executes them locally'''

import sys
from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import Binary
from cPickle import dumps, loads

from mininet.net import Mininet, init
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.clean import cleanup
import mininet.util as util

net = None
cmdDict = {}

class MininetSlaveService:

    def mininetStart(self, ptopo, pcparams):
        '''Start mininet instance with pickled topo and ctrlr params as args'''
        global net
        cparams = loads(pcparams.data)
        topo = loads(ptopo.data)
        c = lambda a: RemoteController(a, defaultIP=cparams[0], port=cparams[1])
        init()
        net = Mininet(topo, switch=OVSKernelSwitch, controller=c, autoSetMacs=True, autoStaticArp=False)
        net.start()
        return

    def mininetStop(self):
        '''Stop the running mininet instance'''
        global net
        if(net is not None):
            net.stop()
        net = None
        cleanup()
        return

    def mininetGetHosts(self):
        '''Returns a pickled list of host names'''
        global net
        if(net is None):
            return Binary(dumps(None))
        return Binary(dumps([h.name for h in net.hosts]))

    def mininetGetSwitches(self):
        '''Returns a pickled list of host names'''
        global net
        if(net is None):
            return Binary(dumps(None))
        return Binary(dumps([s.name for s in net.switches]))

    def getHostIP(self, hostName, intf=None):
        global net
        if(net is None):
            return None
        host = net.nameToNode[hostName]
        if(host is None):
            return None
        return host.IP(intf=intf)

    def getCmd(self, cmd):
        return util.getCmd(cmd)

    def cmdSend(self, hostName, cmd):
        global net
        if(net is None):
            return None
        host = net.nameToNode[hostName]
        if(host is None):
            return None
        c = host.lxcSendCmd(cmd)
        handle = id(c)
        cmdDict[handle] = c
        return handle

    def cmdReadLine(self, handle):
        if(handle not in cmdDict):
            return None
        c = cmdDict[handle]
        return c.readLine()

    def cmdWaitOutput(self, handle):
        if(handle not in cmdDict):
            return None
        c = cmdDict[handle]
        ret = c.waitOutput()
        del cmdDict[handle]
        return ret

    def cmdKill(self, handle):
        if(handle not in cmdDict):
            return None
        c = cmdDict[handle]
        ret = c.kill()
        del cmdDict[handle]
        return ret

    def cmdWait(self, handle):
        if(handle not in cmdDict):
            return None
        c = cmdDict[handle]
        ret = c.wait()
        del cmdDict[handle]
        return ret


# A simple server 
if __name__ == '__main__':
    port = 8000
    if(len(sys.argv) > 1):
        try:
            port = int(sys.argv[1])
        except ValueError:
            print 'Could not convert the argument "%s" to int' % sys.argv[1]
    server = SimpleXMLRPCServer(("localhost", port), logRequests=False, allow_none=True)
    print "Listening on port 8000..."
    # Register functions
    server.register_instance(MininetSlaveService())
    #Happy serving!
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        if(net is not None):
            net.stop()
        net = None
        cleanup()
        print 'Bye bye'
        exit(0)
