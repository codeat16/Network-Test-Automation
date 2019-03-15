import sys
import re
import json

ip_to_host_and_int_file = 'ip_to_host.json'

ip_to_host_and_int = {}
Host_to_Outputfiles = {
    'r1' : None,
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
    'stdout' : None,    
    }

def convert_all_output_files(prefix):

    with open(ip_to_host_and_int_file,'rt') as json_in:
        ip_to_host_and_int = json.load(json_in)

    for host in Host_to_Outputfiles.keys():
        with open( prefix + ' - ' + host +'.txt', 'rt') as fin:
            with open( prefix + ' - ' + host +' w name.txt', 'wt') as fout:
                for line in fin:
                    ip_found = re.findall(r'(\d+\.\d+\.\d+\.\d+)',line)
                    for ip in ip_found:                        
                        if ip in ip_to_host_and_int:
                            line = re.sub( ip, ip+' ['+ip_to_host_and_int[ip]+']', line)
                    fout.write(line)
                           

                        
                        
if __name__ == '__main__':
    convert_all_output_files(sys.argv[1].split('.')[0])
    