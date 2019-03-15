import json
import pprint
from cliconn import CliConn
import sys
import time
import threading

####################
# Global variables #
####################
DEBUG = True
VERIFY_EVERY_COMMIT = True

pre1 = '!---'
post1 = '---!'
pre2 = '!-----'
post2 = '-----!'
threadshared_success = False

# hostname in lower : telnet port number in int. The mapping is read from 'rest.json' which is downloaded
#  from CML simuation.
hostname_to_port = {}

# hostname in lower : cliconn object  
hostname_to_cliconn = {}

# list of three element tuple:
#    (hostname in lower, commands (newline and commit all inclusive), True/False indicates to commit or not)
# The list is constructed from a config file passed in sys.argv[1]
# The config file need to follow the following format:
#   ! at the beginning, '---' or '===' in the line:
#     means comment and and the line is skipped from execution
#   @hostname
#     to indicate the router to configure on
#   commit
#     All commands up to 'commit' will be executed at one cmd() call. Verification action will be done right after
#     depend on the value of VERIFY_EVERY_COMMIT
command_list = []

_CMLServerIP = '1.1.1.1'
_CMLCliUsername = 'user'
_CMLCliPassword = 'pass'
IPallXRouters = [

    '10.0.0.1','10.0.0.2','10.0.0.5','10.0.0.6',
    '10.0.0.9','10.0.0.10','10.0.0.13','10.0.0.14',
    '10.0.0.21','10.0.0.22','10.0.0.25','10.0.0.26',
    '10.0.0.29','10.0.0.30','10.0.0.33','10.0.0.34',
    '10.0.0.37','10.0.0.38','10.0.0.41','10.0.0.42']

IPS1_Hosts = ['10.50.0.1', '10.50.0.2']
IPS2_Hosts = ['10.51.0.1', '10.51.0.2']
IPS3_Hosts = ['10.52.0.1', '10.52.0.2']
IPS4_Hosts = ['10.53.0.1', '10.53.0.2']

Host_to_IPs = {
    'r1' : ['10.0.0.1'],

    's1-host' : ['10.50.0.1', '10.50.0.2'],
    's2-host' : ['10.51.0.1', '10.51.0.2'],
    's3-host' : ['10.52.0.1', '10.52.0.2']],
    's4-host' : ['10.53.0.1', '10.53.0.2'],    
    'p1' : ['10.70.0.1'],
    'p2' : ['10.71.0.1'],    
    'p3' : ['10.72.0.1'],
    'p4' : ['10.73.0.1'],    
    'p5' : ['10.74.0.1'],
    'p6' : ['10.75.0.1'], 
    'p7' : ['10.76.0.1'],    
    'p8' : ['10.77.0.1'],  
    'p9' : ['10.78.0.1'],      
    'p10' : ['10.79.0.1'],  
    'p11' : ['10.80.0.1'],     
    'p12' : ['10.81.0.1'],   
    'p13' : ['10.82.0.1'],    
    }


Hosts_in_Sites = ['s1-host', 's2-host', 's3-host', 's4-host']  

Host_to_Outputfiles = {
    'r1' : None,
    'r2' : None,
    'r3' : None,
    'r4' : None,
    'r5' : None,
    'r6' : None,
    'r7' : None,
    'r8' : None,
    'r9' : None,
    'r10' : None,
    'r11' : None,
    'r12' : None,
    'r13' : None,
    'r14' : None,
    'r15' : None,
    'r16' : None,
    'r17' : None,
    'r18' : None,
    'r19' : None,
    'r20' : None,  
    's1-host' : None,
    's2-host' : None,
    's3-host' : None,
    's4-host' : None,  
    'p1' : None,
    'p2' : None,   
    'p3' : None,
    'p4' : None,    
    'p5' : None,
    'p6' : None,
    'p7' : None,   
    'p8' : None,  
    'p9' : None,     
    'p10' : None, 
    'p11' : None,    
    'p12' : None,    
    'p13' : None,
    }

Hosts_in_PP = [
    'p'+str(x) for x in range(1,14)
	]


# Define the node to open terminal. This prevents opening unnecessary terminals to 
# reduce the chance of terminal stale error:
#  ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it    
Node_of_Interest = Host_to_Outputfiles.keys()

AllXRouters_Hostnames = [
    'r1',
    'r2',
    'r3',
    'r4',
    'r5',
    'r6',
    'r7',
    'r8',
    'r9',
    'r10',
    'r11',
    'r12',
    'r13',
    'r14',
    'r15',
    'r16',
    'r17',
    'r18',
    'r19',
    'r20',
    ]
    
    
def read_commands(command_list):
    
    def err_handler(msg):
        print(msg)
        print(pre1 + 'Successfully parsed up to:' + post1)
        print(command_list)
        raise
        
        
    if len(sys.argv) <= 1:
        print('Missing configfile')
        print('Usage: python3 exec_change.py configfile')
        raise
        
    with open(sys.argv[1],'rt') as f:
        host = ''
        previous_host = ''
        current_command = ''
        
        for line in f:
            if line.isspace() or '---' in line or '===' in line or line.startswith('!') or line.startswith('end'):
                continue
            else:
                if line.startswith('@'):
                    host = line.lstrip('@').rstrip(' \t\n\r').lower()
                    if host in hostname_to_port.keys():
                        if current_command != '':
                            command_list.append( (previous_host, current_command, False ) )
                            current_command = ''
                        previous_host = host
                    else:
                        err_handler(pre1 + 'Incorrect hostname at line: {}'.format(line) + post1)
                elif line.startswith('commit'):
                    current_command += line
                    if previous_host != '' :
                        command_list.append( (previous_host, current_command, True ) )
                        current_command = ''
                    else:
                        err_handler(pre1 + 'No host to commit on at line: {}'.format(line) + post1)
                else:
                    current_command += line
                    
        command_list.append( (previous_host, current_command, False ) )
        
        
def read_ports(hostname_to_port):
    ''' Read the 'rest.jon' file into dictionary
    str(hosname_in_lowercase) : int(TCP port number for Telnet)
	'''
    with open('rest.json','rt') as f:
        s = ''
        for line in f:
            s+=line

    js = json.loads(s)
    
    for key in js.keys():
        try:
            ''' Device not started will not have PortConsole and will cause error in try.
                Not properly started devices will be checked in initial ping
            '''
            nodename=js[key]['NodeName'].split('::')[1].lower()
            ''' Some devices do not have node name and will cause error in try. Example:
                  External Address
                  Forwarding Port on Server
                  Either devices do not require handling
            '''
            if nodename in Node_of_Interest:
                hostname_to_port.update({ nodename : int(js[key]['PortConsole']) })
        except:
            pass

            
def open_all_terminal():
    ''' Open every terminal for future use.
    '''
    print(pre1 + 'open_all_terminal() executing' + post1)
    for hostname in hostname_to_port.keys():
    #for hostname in ['r1']:
        cliconn = CliConn(
            ip=_CMLServerIP,
            username=_CMLCliUsername,
            password=_CMLCliPassword,
            port=hostname_to_port[hostname],
            termtype='telnet')
            
        cliconn.debug = DEBUG
        
        hostname_to_cliconn.update({ hostname : cliconn })
        
    print(pre1 + 'all terminal(s) as below:' + post1)
    pprint.pprint(hostname_to_cliconn)
    
    
def close_all_terminal():
    ''' Close every terminal that is open.
    '''
    print(pre1 + 'close_all_terminal() executing' + post1)
    for cliconn in hostname_to_cliconn.values():
        cliconn.close()


def refresh_all_terminal():
    close_all_terminal()
    #open_all_terminal()
      

def open_all_output_files(prefix):
    for host in Host_to_Outputfiles.keys():
        Host_to_Outputfiles[host] = open( prefix + ' - ' + host +'.txt', 'wt')
    
    
def close_all_output_files(prefix):
    for host in Host_to_Outputfiles.keys():
        Host_to_Outputfiles[host].close()
    
    
def assert_ping(src_name,src_ips,dest_ips):
    ''' Matrix ping from source(s) to destination(s).
	Return True only if every ping is successful.
	The reason for mixing name and IP is due to the nature of modeling, where ssh target
	is easir to reference by name. While inside ssh/telnet session, name is not recognized and ip address
	need to be used instead
	Args:
	    src_name: hostname of the source device to ping from
	    src_ips: a list of source ip addresses
	    dest_ips: a list of destination ip addresses
	'''
    cliconn = hostname_to_cliconn[src_name]
    outputfile = Host_to_Outputfiles[src_name]
    #success = True
    
    for src_ip in src_ips:
        for dest_ip in dest_ips:
            cliconn.outputfile = outputfile
            result = cliconn.cmd('ping {} source {} count 20 validate'.format(dest_ip,src_ip))
            outputfile.write(result +'\n')
            print(result)
            if not "100 percent" in result:
                #success = False
                threadshared_success = False
                if DEBUG:
                    print(pre2 + 'ping failure' + post2)
                    outputfile.write(pre2 + 'ping failure' + post2 +'\n')
                    print(success)   
                    outputfile.write(str(success) +'\n')

    #return success


def assert_trace(src_name,src_ips,dest_ips):
    ''' Matrix trace from source(s) to destination(s).

	Args:
	    src_name: hostname of the source device to ping from
	    src_ips: a list of source ip addresses
	    dest_ips: a list of destination ip addresses
	'''
    cliconn = hostname_to_cliconn[src_name]
    outputfile = Host_to_Outputfiles[src_name]
    
    for src_ip in src_ips:
        for dest_ip in dest_ips:
            cliconn.outputfile = outputfile
            # original version, running great but have timeout in 1st multithread version
            #result = cliconn.cmd('trace {} source {} maxttl 7 timeout 2 probe 2'.format(dest_ip,src_ip))
            # tuning for multithread version
            result = cliconn.cmd('trace {} source {} maxttl 7 timeout 4 probe 2'.format(dest_ip,src_ip))
            outputfile.write(result +'\n')
            print(result)

            
def assert_route(router_host):
    ''' show applicable route or bgp command for router

	Args:
	    router_host: hostname of router
	'''
    cliconn = hostname_to_cliconn[router_host]
    outputfile = Host_to_Outputfiles[router_host]
    
    cliconn.outputfile = outputfile
    result = cliconn.cmd('show route')
    outputfile.write(result +'\n')
    print(result)
    
	
def group_assert_ping(src_host, Hosts):
    ''' for threaded use
    '''
    for dest_host in Hosts:
        print(pre1 + 'pinging from {} to {} '.format(src_host, dest_host) + post1)  
        assert_ping(src_host, Host_to_IPs[src_host], Host_to_IPs[dest_host] )
                

def group_assert_trace(src_host, Hosts):
    ''' for threaded use
    '''
    for dest_host in Hosts:
        print(pre1 + 'tracing from {} to {} '.format(src_host, dest_host) + post1)
        assert_trace(src_host, Host_to_IPs[src_host], Host_to_IPs[dest_host])
         
                
def verify_connectivity(checkpoint_title):
    ''' Startup routine to verify simulation is running well.
    This is done to protect against the known bug of sometime devices do not load
    configuration correctly.
    
    Also serve to confirm the connectivity for all network devices as host end-to-end.
    '''
    threadshared_success = True
    
    print(pre1 + 'pinging from r1 to IPallXRouters' + post1)
    Host_to_Outputfiles['r1'].write(pre1+ 'verify_connectivity({})'.format(checkpoint_title) +post1+'\n')
    
    t = threading.Thread( target = assert_ping, args = ['r1',Host_to_IPs['r1'],IPallXRouters] )
    t.start()

    for src_host in Hosts_in_Sites:
        Host_to_Outputfiles[src_host].write(pre1+ 'verify_connectivity({})'.format(checkpoint_title) +post1+'\n')
        
        t = threading.Thread( target = group_assert_ping, args = [src_host, Hosts_in_PP] )
        t.start()
 
    while threading.active_count() > 1:
        pass
        
    # reverse ping optional
    '''
    for src_host in Hosts_in_PP:
        Host_to_Outputfiles[src_host].write(pre1+ 'verify_connectivity({})'.format(checkpoint_title) +post1+'\n')
        for dest_host in Hosts_in_Sites:
            print(pre1 + 'pinging from {} to {} '.format(src_host, dest_host) + post1)  
            if not assert_ping(src_host, Host_to_IPs[src_host], Host_to_IPs[dest_host]):
                success = False
    '''
    return threadshared_success
    
    
def verify_trace(checkpoint_title):
    
    for src_host in Hosts_in_Sites:
        Host_to_Outputfiles[src_host].write(pre1+ 'verify_trace({})'.format(checkpoint_title) +post1+'\n')
        t = threading.Thread( target = group_assert_trace, args = [src_host, Hosts_in_PP] )
        t.start()
    
    for src_host in Hosts_in_PP:
        Host_to_Outputfiles[src_host].write(pre1+ 'verify_trace({})'.format(checkpoint_title) +post1+'\n')
        t = threading.Thread( target = group_assert_trace, args = [src_host, Hosts_in_Visa] )
        t.start()

    while threading.active_count() > 1:
        pass            

        
def verify_route(checkpoint_title):
    
    for router_host in AllXRouters_Hostnames:
        Host_to_Outputfiles[router_host].write(pre1+ 'verify_route({})'.format(checkpoint_title) +post1+'\n')
        t = threading.Thread( target = assert_route, args = [router_host] )
        t.start()
        # tuning for multithread version
        time.sleep(5)

    while threading.active_count() > 1:
        pass
        
        
''' Main code 
'''
read_ports(hostname_to_port)
if DEBUG:
    pprint.pprint(hostname_to_port)
    
read_commands(command_list)
pprint.pprint(command_list)

try:
    open_all_output_files(sys.argv[1].split('.')[0])
    open_all_terminal()
    
    # initial verification
    print(pre1 + '***Precheck***' + post1)
    if not verify_connectivity('***Precheck***'):
        print(pre2 + 'Connectivity precheck failed' + post2)

    refresh_all_terminal()
    
    verify_trace('***Precheck***')
    verify_route('***Precheck***')    

    # commands execution
    print(pre1 + '***Execution***' + post1)        
    for hostname,cmds,to_commit in command_list:
        cliconn = hostname_to_cliconn[hostname]

        if to_commit:
            cmdlist = cmds.split('\n')
            for cmd in cmdlist:
                if cmd != '':
                    result = cliconn.cmd(cmd+'\n')
                    print(result)
            
            print(pre1 + 'Wait 30 seconds for convergence before verifying connectivity.' + post1)
            time.sleep(30)
            result = cliconn.cmd('end\n')
            print(result)                    
            print(pre1 + 'Commit completed, checking connectivity...' + post1)
 
            if VERIFY_EVERY_COMMIT:
            
                refresh_all_terminal()
                
                if not verify_connectivity(hostname+'\n'+cmds):
                    print(pre2 + 'Connectivity commit check failed' + post2)
                    print(pre2 + hostname + '\n' + cmds + post2)
                
        else:
            cmdlist = cmds.split('\n')
            for cmd in cmdlist:
                if cmd != '':
                    result = cliconn.cmd(cmd+'\n')
                    print(result)
                    
    # final verification   
    print(pre1 + '***Postcheck***' + post1)    
    
    refresh_all_terminal()

    if not verify_connectivity('***Postcheck***'):
        print(pre2 + 'Connectivity postcheck failed' + post2)
    
    refresh_all_terminal()
    
    verify_trace('***Postcheck***')
    verify_route('***Postcheck***')    

finally:
    close_all_terminal()
    close_all_output_files(sys.argv[1].split('.')[0])



