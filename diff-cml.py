from subprocess import call
import sys



def is_ignored_toplevel(line):
    ignored_starts = [
        'clock',
        'banner',
        '*',
        '^C',
        '$',
        'logging',
        'usergroup',
        'tacacs',
        'aaa',
        'line ',
        'snmp-server',
        'tftp',
        'flow',
        'sampler-map',
        'interface tunnel',
        'ssh',
        'control-plane',
        'telnet',
        'domain',
        ]
    for ignored_start in ignored_starts:
        if line.startswith(ignored_start):
            return True
    return False
    

def is_ignored_any(line):
    ignored_starts = [
        ' bandwidth',
        ' service-policy',
        ' flow ipv4',
        ' password',
        ]
    for ignored_start in ignored_starts:
        if line.startswith(ignored_start):
            return True
    return False

    
def strip_ignored_section(file_in, file_out):
    with open(file_in, 'rt') as fin:
        with open(file_out, 'wt') as fout:
            current_section = [''] * 20
            
            for line in fin:
                section_level = line.find( line.lstrip(' ') )
                current_section [ section_level ] = line
                for i in range(section_level+1,10):
                    current_section[i] = ''
                if is_ignored_toplevel( current_section[0] ):
                    pass
                elif is_ignored_any( line ):
                    pass                   
                else:
                    fout.write(line)
                    
                    
if __name__ == '__main__':
    left_filename = sys.argv[1]
    right_filename = sys.argv[2]
    
    strip_ignored_section(left_filename, '__left.txt')
    strip_ignored_section(right_filename, '__right.txt')
    
    call( ['diffuse','__left.txt','__right.txt'] )
    