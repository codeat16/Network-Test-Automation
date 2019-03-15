import json
import sys
import pprint
import re
import itertools

DEBUG = False

def read_interface_mapping():
    with open('cml_interface_map.json','rt') as f:
        s = ''
        for line in f:
            s+=line

    return json.loads(s)

    
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
    
    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Missing configfile')
        print('Usage: python3 convert_completeconfigfile_to_cml.py input_config_file')
        raise
    
    interface_mapping = read_interface_mapping()
    if DEBUG:
        pprint.pprint(interface_mapping)

    fin_name = sys.argv[1]
    fout_name = sys.argv[1].rstrip('.txt')+' - cml.txt'
    prevline_int_matched = False
    
    with open(fin_name,'rt') as fin:
        with open(fout_name,'wt') as fout:
            host = ''
            
            for line,nextline in pairwise(fin):
                # run 1: checking host identifier
                if line.startswith('hostname'):
                    host = line.lstrip('hostname').lstrip(' \t\n\r').rstrip(' \t\n\r').lower()
                    
                # run 2: matching interface
                int_te_matched = re.match(r'([Tt][Ee]\w*)(\d+/\d+/\d+/\d+)', line)
                if not int_te_matched:
                    int_te_matched = re.search(r'[\s]+([Tt][Ee]\w*)(\d+/\d+/\d+/\d+)', line)
             
                int_ge_matched = re.match(r'([Gg]\w*)(\d+/\d+/\d+/\d+)', line)                
                if not int_ge_matched:
                    int_ge_matched = re.search(r'[\s]+([Gg]\w*)(\d+/\d+/\d+/\d+)', line)  
                    
                int_mgmt_matched = re.search(r'MgmtEth', line)
                
                # run 3: write output
                if int_te_matched:
                    if nextline.lstrip(' \t\n\r').rstrip(' \t\n\r').lower() == 'shutdown':
                        #fout.write( '!' + line ) 
                        # instead of making the line comment, just pass
                        pass
                    else:
                        interface_prod = 'TenGigE'+int_te_matched.group(2)
                        interface_cml = interface_mapping[host][interface_prod]
                        fout.write( line.replace(int_te_matched.group(1)+int_te_matched.group(2), interface_cml) )
                    prevline_int_matched = True
                elif int_ge_matched:
                    if nextline.lstrip(' \t\n\r').rstrip(' \t\n\r').lower() == 'shutdown':
                        #fout.write( '!' + line ) 
                        # instead of making the line comment, just pass    
                        pass
                    else:
                        interface_prod = 'GigabitEthernet'+int_ge_matched.group(2)
                        interface_cml = interface_mapping[host][interface_prod]
                        fout.write( line.replace(int_ge_matched.group(1)+int_ge_matched.group(2), interface_cml) )  
                    prevline_int_matched = True
                elif int_mgmt_matched:
                    if nextline.lstrip(' \t\n\r').rstrip(' \t\n\r').lower() == 'shutdown':
                        #fout.write( '!' + line ) 
                        # instead of making the line comment, just pass
                        pass
                    prevline_int_matched = True
                else:
                    if line.lstrip(' \t\n\r').rstrip(' \t\n\r').lower() == 'shutdown' and prevline_int_matched:
                        #fout.write( '!' + line )
                        # instead of making the line comment, just pass
                        pass
                    else:
                        fout.write(line)
                    prevline_int_matched = False
                    
    print('File "{}" converted and saved as new file "{}"'.format(fin_name,fout_name))           

    if True:
        fin_name = sys.argv[1].rstrip('.txt')+' - cml.txt'
        fout_name = sys.argv[1].rstrip('.txt')+' -- cml.txt'
        
        int_list = []
        int_configs = {}
        in_section_loopback = False
        in_section_int = False
        in_section_ospf = False
        in_section_ospf_int = False
        
        with open (fin_name,'rt') as fin:
            with open(fout_name,'wt') as fout:
                for line,nextline in pairwise(fin):
                    if 'interface Loopback' in line:
                        in_section_loopback = True
                        fout.write(line)
                    elif 'prefix-set' in line:
                        if in_section_int:
                            # write
                            int_list_sorted = sorted(int_list)
                            for int_key in int_list_sorted:
                                fout.write( int_configs[int_key])
                                
                            # flush 
                            int_list = []
                            int_configs = {}
                            in_section_loopback = False
                            in_section_int = False
                        fout.write(line)
                    elif line.startswith('router ospf'):
                        in_section_ospf = True
                        fout.write(line)
                    elif line.startswith('!'):
                        if in_section_ospf:
                            # write
                            int_list_sorted = sorted(int_list)
                            for int_key in int_list_sorted:
                                fout.write( int_configs[int_key])
                            # flush 
                            int_list = []
                            int_configs = {} 
                            in_section_ospf = False
                            in_section_ospf_int = False
                        elif in_section_loopback:
                            if 'GigabitEthernet' in nextline:
                                in_section_int = True
                                in_section_loopback = False
                        elif in_section_int:
                            int_configs[int_key] += line
                        fout.write(line)
                        
                    elif in_section_int or in_section_ospf_int:
                        if 'GigabitEthernet' in line:
                            int_key = re.search(r'(GigabitEthernet\d+/\d+/\d+/\d+\.*\d*)',line).group(1)
                            int_list.append( int_key )
                            int_configs.update( {int_key : line} )
                        else:
                            int_configs[int_key] += line
                            
                    elif in_section_ospf:
                        if 'GigabitEthernet' in nextline:
                            in_section_ospf_int = True
                        fout.write(line)
                  
                    else:
                        fout.write(line)

        print('File "{}" further converted and saved as new file "{}"'.format(fin_name,fout_name))   
