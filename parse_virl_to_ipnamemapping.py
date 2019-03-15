import xml.etree.ElementTree as ET
import re
import json

virl_file = 'example.virl'
ip_to_host_and_int_file = 'example ip_to_host.json'

tree = ET.parse(virl_file)
root = tree.getroot()

hostname_to_config = {}
ip_to_host_and_int = {}

for child in root:
    if child.tag.endswith('group'):
        for gchild in child:
            if gchild.tag.endswith('node'):
                host = gchild.attrib['name'].lower()
                for ggchild in gchild:
                    if ggchild.tag.endswith('extensions'):
                        for gggchild in ggchild:
                            if gggchild.tag.endswith('entry'):
                                if gggchild.attrib['type'] == 'String':
                                    config = gggchild.text
                                    hostname_to_config.update( {host : config} )

for host in hostname_to_config.keys():
    
    current_section = [''] * 20
    
    for line in hostname_to_config[host].split('\n'):
        #init section
        section_level = line.find( line.lstrip(' ') )
        current_section [ section_level ] = line
        for i in range(section_level+1,10):
            current_section[i] = ''
        if line.startswith(' ipv4 address'):
            interface = current_section[0].rstrip('\n')[10:]
            ip = re.search(r'(\d+\.\d+\.\d+\.\d+)',line).group(1)
       
            ##ip_to_host_and_int.update( { ip : host+' '+interface } )
            ip_to_host_and_int.update( { ip : host } )
            
with open(ip_to_host_and_int_file,'wt') as fout:
    json.dump(ip_to_host_and_int, fout)

with open(ip_to_host_and_int_file,'rt') as fin:
    d=json.load(fin)
    for key,value in d.items():
        print(key,value)
                              
    
