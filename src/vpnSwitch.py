# encoding: utf-8
import sys
import re
import subprocess
import argparse
from workflow import Workflow


VPN_CONTROL_START = '-on'
VPN_CONTROL_STOP = '-off'

ICON_ON_ORDERLY = './vpn_on_orderly.png'
ICON_OFF_CURRENT = './vpn_off_current.png'
ICON_ON = './vpn_on.png'
ICON_OFF = './vpn_off.png'

VPN_TYPE_L2TP = 'L2TP'

def search_key_for_vpn(vpnInfo):
     """Generate a string search key for a post"""
     elements = []
     elements.append(vpnInfo['name'])  # name of vpn
     elements.append(vpnInfo['type'])  # type of vpn
     return u' '.join(elements)

def vpnConnectStatus(vpnId):
    process = subprocess.Popen('scutil --nc status ' + vpnId, shell=True,
        stdout=subprocess.PIPE)
    status = process.stdout.readline().strip().lower()
    return status

def connect(workflow, vpnId, vpnType):
    cmd = 'scutil --nc start ' + vpnId
    if vpnType == VPN_TYPE_L2TP:
        secretKey = workflow.settings.get('l2tp_shared_secret_key', None)
        if not secretKey:
            return
        cmd += ' --secret ' + 'greenvpn'

    process = subprocess.Popen(cmd, shell=True)

def connectSequence(workflow, vpnIds, vpnTypes):
    count = 0
    for vpnId in vpnIds:
        connect(workflow, vpnId, vpnTypes[count])
        count += 1
        # loop to check status.
        isConnected = False
        while True:
            time.sleep(0.5)
            connectStatus = vpnConnectStatus(vpnId)
            if connectStatus == 'connected':
                isConnected = True
                break
            elif connectStatus == 'disconnected':
                break

        if isConnected:
            break

def disconnect(vpnId):
    process = subprocess.Popen('scutil --nc stop ' + vpnId, shell=True)

def main(workflow):
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?')
    parser.add_argument('--action', nargs='?', default=None)
    parser.add_argument('--setkey', dest='l2tpkey', nargs='?', default=None)
    args = parser.parse_args(workflow.args)

    if args.l2tpkey:
        workflow.settings['l2tp_shared_secret_key'] = args.l2tpkey
        return 0

    if not args.action:
        queryKey = args.query
        vpnList = []

        process = subprocess.Popen('scutil --nc list', shell=True, stdout=subprocess.PIPE)
        process.stdout.readline()
        patternName = re.compile(r'".+"')
        patternId = re.compile(r'[\w]+-[\w]+-[\w]+-[\w]+-[\w]+')
        patternType = re.compile(r'\[.+\]')
        patternStatus = re.compile(r'\*\ \(.+\)')
        while True:
            line = process.stdout.readline()
            # print line
            if len(line) > 0:
                vpnId = patternId.search(line).group()
                vpnName = patternName.search(line).group()[1:-1]
                vpnType = patternType.search(line).group()[1:-1].split(':')[1]
                vpnStatus = patternStatus.search(line).group()[3:-1].lower()
                vpnInfo = {'id':vpnId, 'name':vpnName, 'type':vpnType, 'status':vpnStatus}
                # print vpnInfo
                vpnList.append(vpnInfo)
            elif process.poll() != None:
                break

        # add switch on vpn orderly item if possible.
        if queryKey != None and len(queryKey) <=3 and VPN_CONTROL_START.startswith(queryKey):
            connectedVpn = None
            vpnIds = []
            vpnTypes = []
            for item in vpnList:
                if item['status'] == 'connected':
                    connectedVpn = item
                    break
                else:
                    vpnIds.append(item['id'])
                    vpnTypes.append(item['type'])

            if connectedVpn == None:
                actionArg = 'onsequence,' + ':'.join(vpnIds) + ',' + ':'.join(vpnTypes)
                workflow.add_item(title='Start vpn orderly',
                    subtitle='try to switch vpn on orderly in the following list until success',
                    icon=ICON_ON_ORDERLY, arg=actionArg, valid=True)

        # add switch off item if possible.
        if queryKey != None and len(queryKey) <=4 and VPN_CONTROL_STOP.startswith(queryKey):
            connectedVpn = None
            for item in vpnList:
                if item['status'] == 'connected':
                    connectedVpn = item
                    break
            if connectedVpn != None:
                actionArg = 'off,' + connectedVpn['id'] + ',' + connectedVpn['type']
                workflow.add_item(title='Stop ' + connectedVpn['name'],
                    subtitle='switch off current connected vpn', icon=ICON_OFF_CURRENT,
                    arg=actionArg, valid=True)

        if queryKey != None and len(queryKey) != 0:
            vpnList = workflow.filter(queryKey, vpnList, key=search_key_for_vpn, min_score=20)

        for item in vpnList:
            subtitle = '(' + item['status'] + ')' + item['type']
            actionArg = 'on,' + item['id'] + ',' + item['type']
            icon = ICON_ON if item['status'] == 'connected' else ICON_OFF
            workflow.add_item(title=item['name'], subtitle=subtitle, icon=icon,
                arg=actionArg, valid=True)

        workflow.send_feedback()
        return 0
    else:
        # Do action to switch vpn.
        vpnControl, vpnId, vpnType = args.query.split(',')
        if vpnControl == 'on':
            connect(workflow, vpnId, vpnType)
        elif vpnControl == 'onsequence':
            vpnIds = vpnId.split(':')
            vpnTypes = vpnType.split(':')
            connectSequence(workflow, vpnIds, vpnTypes)
        else:
            disconnect(vpnId)
        return 0


if __name__=="__main__":
    workflow = Workflow()
    sys.exit(workflow.run(main))
