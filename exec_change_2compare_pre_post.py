import sys
from subprocess import call
#import re
#import json

#ip_to_host_and_int_file = 'ip_to_host.json'

ip_to_host_and_int = {}
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

def compare_output_pre_and_post(prefix):

    #with open(ip_to_host_and_int_file,'rt') as json_in:
    #    ip_to_host_and_int = json.load(json_in)

    for host in Host_to_Outputfiles.keys():
        if host.startswith('rt'):
            name_fin = prefix + ' - ' + host +'.txt'
            name_fout_pre = 'tmp--'+ prefix + ' - ' + host +' - pre.txt'
            name_fout_post = 'tmp--'+ prefix + ' - ' + host +' - post.txt'        
        else:
            name_fin = prefix + ' - ' + host +' w name.txt'
            name_fout_pre = 'tmp--'+ prefix + ' - ' + host +' w name - pre.txt'
            name_fout_post = 'tmp--'+ prefix + ' - ' + host +' w name - post.txt'
        
        with open( name_fin, 'rt') as fin:
            with open( name_fout_pre, 'wt') as fout_pre:
                with open( name_fout_post, 'wt') as fout_post:
                    in_precheck = False
                    in_postcheck = False
                    
                    for line in fin:
                        if 'verify_' in line:
                            if 'Precheck' in line:
                                in_precheck = True
                                in_postcheck = False
                            elif 'Postcheck' in line:
                                in_precheck = False
                                in_postcheck = True
                            else:
                                in_precheck = False
                                in_postcheck = False                            
                                
                        if in_precheck:
                            fout_pre.write(line)
                        elif in_postcheck:
                            fout_post.write(line)
            
        # Notepad++
        #  pros and cons: reverse of that diffuse
        #callcmd = [r'C:\Program Files (x86)\Notepad++\notepad++.exe',name_fout_pre,name_fout_post]
        # diffuse 0.4.8, latest version as of Oct 7, 2016
        #   pros: work better in highlight particular word
        #   cons: does not match well for ocx hosts's output when the bug in "exec_change_1addname_to_output.py"
        #         that does not dealing with muliple ip in one line
        callcmd = ['diffuse',name_fout_pre,name_fout_post]
        call( callcmd )

                        
                        
if __name__ == '__main__':
    compare_output_pre_and_post(sys.argv[1].split('.')[0])
    