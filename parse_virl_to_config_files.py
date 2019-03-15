import xml.etree.ElementTree as ET

virl_file = 'example.virl'

tree = ET.parse(virl_file)
root = tree.getroot()

for child in root:
    if child.tag.endswith('group'):
        for gchild in child:
            if gchild.tag.endswith('node'):
                host = gchild.attrib['name'].lower()
                print(host)
                for ggchild in gchild:
                    if ggchild.tag.endswith('extensions'):
                        for gggchild in ggchild:
                            if gggchild.tag.endswith('entry'):
                                if gggchild.attrib['type'] == 'String':
                                    config = gggchild.text
                                    with open('example - '+ host + '.txt','wt') as fout:
                                        fout.write(config)
                                    
    
