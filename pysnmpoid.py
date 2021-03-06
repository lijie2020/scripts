from pysnmp.entity.rfc3413.oneliner import cmdgen
import time,os
import re
import json
import multiprocessing

networkInterfaceTemplate = [
        {
            'id':(1,3,6,1,2,1,2,2,1,1),
            'name':'network',
            'outValue':('ifBytesOut','ifBytesIn','ifStatus'),
            'outPattern':'snmp.{0[config][target]}.{0[data][ifName]}.{1}'
        },
        {
            'ifName':(1,3,6,1,2,1,2,2,1,2),
            'ifStatus':(1,3,6,1,2,1,2,2,1,8),
            'ifBytesIn':(1,3,6,1,2,1,31,1,1,1,6),
            'ifBytesOut':(1,3,6,1,2,1,31,1,1,1,10)
        }
    ]
#snmpConfig = [
#        {
#            'target':'127.0.0.1',
#            'community':'public_kingsoft',
#            'templates':[networkInterfaceTemplate,]
#        }
#    ]

#ips = hosts_hz.hosts()
ips = {'10.10.0.1':'xxxx'}

snmpConfig = list()
for target in ips.keys():
    community = ips[target]
    d = dict()
    d['target'] = target
    d['community'] = ips[target]
    d['templates'] = [networkInterfaceTemplate,]
    snmpConfig.append(d)

def snmp_walk(snmpTarget,snmpCommunity,plainOID):
    errorIndication,errorStatus, \
        errorIndex, varBindTable = cmdgen.CommandGenerator().nextCmd(
        cmdgen.CommunityData('test-agent',snmpCommunity),
        cmdgen.UdpTransportTarget((snmpTarget,161,)),
    plainOID
    )
    if errorIndication:
        print snmpTarget,errorIndication
    else:
        if errorStatus:
            print '%s at %s\n' % (
                errorStatus.prettyPrint(),
                errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                )
        else:
            return varBindTable

def fetch(config):
    snmpTarget = config['target']
    snmpCommunity = config['community']
    L = list()
    for template in config['templates']:
        snmpTable = dict()
        templateName = template[0]['name']
        snmpTable[templateName] = dict()

        if 'id' in template[0]:
            snmpIdentifierOid = template[0]['id']
            configTable = snmp_walk(snmpTarget,snmpCommunity,snmpIdentifierOid)
            for configValue in configTable:
                snmpTable[templateName][configValue[0][1]] = dict()
        for snmpName,snmpOid in template[1].iteritems():
            dataTable = snmp_walk(snmpTarget,snmpCommunity,snmpOid)
            for row in dataTable:
                for name,val in row:
                    snmpTable[templateName][name[-1]][snmpName] = [name,val]

        d = dict()
        for interface in snmpTable['network'].keys():

            #print snmpTable['network'][interface]['ifName'][1],snmpTable['network'][interface]['ifStatus'][0],snmpTable['network'][interface]['ifStatus'][1]
            port = str(snmpTable['network'][interface]['ifName'][1])
            ifStatusoid = str(snmpTable['network'][interface]['ifStatus'][0])
            ifBytesInoid = str(snmpTable['network'][interface]['ifBytesIn'][0])
            ifBytesOutoid = str(snmpTable['network'][interface]['ifBytesOut'][0])
            ifStatusvalue = int(snmpTable['network'][interface]['ifStatus'][1])
            ifBytesInvalue = int(snmpTable['network'][interface]['ifBytesIn'][1])
            ifBytesOutvalue = int(snmpTable['network'][interface]['ifBytesOut'][1])
            d[port] = {'ifStatus':(ifStatusoid,ifStatusvalue),'ifBytesIn':(ifBytesInoid,ifBytesInvalue),'ifBytesOut':(ifBytesOutoid,ifBytesOutvalue)}
        host = dict()
        host[snmpTarget]=d
        f = open('snmp_port.txt','a')
        f.write(json.dumps(host))
        f.close()

if os.path.isfile('snmp_port.txt'):
            os.remove('snmp_port.txt')
while len(snmpConfig) != 0:
    jobs = []
    for i in xrange(50):
        if len(snmpConfig) !=0:
            config = snmpConfig.pop()
            t = multiprocessing.Process(target=fetch,args=(config,))
            jobs.append(t)
    for t in jobs:
        t.start()

