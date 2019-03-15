import json
import sys
import pprint
import re

DEBUG = False

def read_interface_mapping():
    with open('cml_interface_map.json','rt') as f:
        s = ''
        for line in f:
            s+=line

    return json.loads(s)

    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('Missing configfile')
        print('Usage: python3 convert_config_to_cml.py input_config_file')
        raise
    
    interface_mapping = read_interface_mapping()
    if DEBUG:
        pprint.pprint(interface_mapping)

    fin_name = sys.argv[1]
    fout_name = sys.argv[1].rstrip('.txt')+' - cml.txt'

    
    with open(fin_name,'rt') as fin:
        with open(fout_name,'wt') as fout:
            host = ''
            
            for line in fin:
                # run 1: checking host identifier
                if line.startswith('@'):
                    host = line.lstrip('@').rstrip(' \t\n\r').lower()
                    
                # run 2: matching interface
                int_te_matched = re.match(r'([Tt][Ee]\w*)(\d+/\d+/\d+/\d+)', line)
                if not int_te_matched:
                    int_te_matched = re.search(r'[\s]+([Tt][Ee]\w*)(\d+/\d+/\d+/\d+)', line)
             
                int_ge_matched = re.match(r'([Gg]\w*)(\d+/\d+/\d+/\d+)', line)                
                if not int_ge_matched:
                    int_ge_matched = re.search(r'[\s]+([Gg]\w*)(\d+/\d+/\d+/\d+)', line)  
                
                # run 3: write output
                if int_te_matched:
                    interface_prod = 'TenGigE'+int_te_matched.group(2)
                    interface_cml = interface_mapping[host][interface_prod]
                    fout.write( line.replace(int_te_matched.group(1)+int_te_matched.group(2), interface_cml) )
                elif int_ge_matched:
                    interface_prod = 'GigabitEthernet'+int_ge_matched.group(2)
                    interface_cml = interface_mapping[host][interface_prod]
                    fout.write( line.replace(int_ge_matched.group(1)+int_ge_matched.group(2), interface_cml) )                
                else:
                    fout.write(line)
                    
    print('File "{}" converted and saved as new file "{}"'.format(fin_name,fout_name))           
    
 