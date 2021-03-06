from pysnmp.entity.rfc3413.oneliner import cmdgen
import time
import socket

def snmp_get(snmpTarget, snmpCommunity,oid):

    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData(snmpCommunity),
        cmdgen.UdpTransportTarget((snmpTarget, 161)),
        #cmdgen.MibVariable('SNMPv2-MIB', 'sysName', 0),
        oid,
        timeout = 40,
   )

    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex)-1] or '?'
                )
            )
        else:
            for name, val in varBinds:
                val = val.prettyPrint()
    return val
carbonAddress = '10.0.1.103'
graphiteSocket = socket.create_connection((carbonAddress,2003))
snmpTarget = '10.10.0.1'
snmpCommunity = 'xxxxx'

Interfaces = {'Ten-GigabitEthernet1/3/0/2': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.197', 640434244077977], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.197', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.197', 3042694540981945]}, 'Ten-GigabitEthernet1/3/0/1': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.196', 958144202129097], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.196', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.196', 3069018695490305]}, 'Ten-GigabitEthernet2/4/0/1': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.1431', 4417235295513], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.1431', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.1431', 1765456869778690]}, 'Ten-GigabitEthernet1/4/0/21': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.281', 30347041], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.281', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.281', 982552944765115]}, 'Ten-GigabitEthernet2/4/0/21': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.1451', 29662541], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.1451', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.1451', 961541375844264]}, 'Ten-GigabitEthernet1/4/0/1': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.261', 52258640], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.261', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.261', 1736980645566913]}, 'Ten-GigabitEthernet2/3/0/1': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.1366', 1170712248450355], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.1366', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.1366', 2809170171813087]}, 'Ten-GigabitEthernet2/3/0/2': {u'ifBytesOut': [u'1.3.6.1.2.1.31.1.1.1.10.1367', 26760680884920], u'ifStatus': [u'1.3.6.1.2.1.2.2.1.8.1367', 1], u'ifBytesIn': [u'1.3.6.1.2.1.31.1.1.1.6.1367', 959757466385733]}}
for key in Interfaces.keys():
    t = str(int(time.time()))
    for item in Interfaces[key]:
        L = []
        oidstr = Interfaces[key][item][0].split('.')
        for char in oidstr:
            L.append(int(char))
        oid = tuple(L) 
        value = snmp_get(snmpTarget,snmpCommunity,oid)
        graphiteString = ['snmp']
        graphiteString.append(snmpTarget)
        graphiteString.append(key)
        graphiteString.append(item)
        #graphiteString.append(int(time.time()))
        #graphiteString.append('\n')
        graphiteOutput = '.'.join(str(i) for i in graphiteString) + ' ' + str(value) + ' ' + t + '\n'
        print graphiteOutput
        graphiteSocket.send(graphiteOutput)

        #print graphiteOut
