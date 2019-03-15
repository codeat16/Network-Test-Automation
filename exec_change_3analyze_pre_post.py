import sys
import re

pre1 = '!---'
post1 = '---!'
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
    #'stdout' : None,    
    }

def read_output_to_dict(result_dict, f):
    in_cmd = False
    for line in f:
        if line.startswith('!---------sending "'):
            cmd = line[len('!---------sending "'):]
            in_cmd = True
            result_dict.update( {cmd: [line]} )
        elif line.startswith('!---'):
            in_cmd = False
        elif line.isspace():
            pass
        elif in_cmd:
            result_dict[cmd].append(line)
        else:
            pass
           
def print_result(title, id_1, list_1, id_2, list_2):
    print('')
    print(pre1+ title +post1)
    print(pre1+ id_1 +post1)
    for line in list_1:
        print(line.rstrip('\n'))
    print(pre1+ id_2 +post1)
    for line in list_2:
        print(line.rstrip('\n'))    
    
def analyze_output_pre_and_post(prefix):
    #
    for host in Host_to_Outputfiles.keys():
    
        print('\n\nAnalyzing {}...'.format(host))
        
        output_pre = {}
        output_post = {}
        
        if host.startswith('rt'):
            name_f_pre = 'tmp--'+ prefix + ' - ' + host +' - pre.txt'
            name_f_post = 'tmp--'+ prefix + ' - ' + host +' - post.txt'        
        else:
            name_f_pre = 'tmp--'+ prefix + ' - ' + host +' w name - pre.txt'
            name_f_post = 'tmp--'+ prefix + ' - ' + host +' w name - post.txt'
        

        with open(name_f_pre, 'rt') as f_pre:
            read_output_to_dict(output_pre, f_pre)
        with open(name_f_post, 'rt') as f_post:
            read_output_to_dict(output_post, f_post)
        
        # analyze ping
        output_pre_ping = { key:value for key,value in output_pre.items() if key.startswith('ping') }
        output_post_ping = { key:value for key,value in output_post.items() if key.startswith('ping') }

        for key in output_pre_ping.keys():
            ping_result_pre = [line for line in output_pre_ping[key] if line.__contains__('Success rate')][0]
            ping_result_post = [line for line in output_post_ping[key] if line.__contains__('Success rate')][0]
            ping_result_pre_rate = re.search(r'rate is (\d+) percent', ping_result_pre).group(1)
            ping_result_post_rate = re.search(r'rate is (\d+) percent', ping_result_post).group(1)
            if int(ping_result_pre_rate) != 100 or int(ping_result_post_rate) != 100:
                print_result('ping failure','precheck result',output_pre_ping[key],'postcheck result',output_post_ping[key])
              
        # analyze trace            
        output_pre_trace = { key:value for key,value in output_pre.items() if key.startswith('trace') }
        output_post_trace = { key:value for key,value in output_post.items() if key.startswith('trace') }
        #print(output_pre_trace)
        #print(output_post_trace)
        for key in output_pre_trace.keys():
            trace_seq_pre = [line for line in output_pre_trace[key] if re.search(r'\d+[ \t]+\d+\.\d+\.\d+\.\d+',line)]
            #print(trace_seq_pre)
            trace_seq_post = [line for line in output_post_trace[key] if re.search(r'\d+[ \t]+\d+\.\d+\.\d+\.\d+',line)]
            
            if len(trace_seq_pre) != len(trace_seq_post):
                print_result('trace: number of hops different','precheck result',output_pre_trace[key],'postcheck result',output_post_trace[key])
            else:
                for i in range(len(trace_seq_pre)):
                    ip_pre = re.search(r'\d+[ \t]+(\d+\.\d+\.\d+\.\d+)',trace_seq_pre[i]).group(1)
                    ip_post = re.search(r'\d+[ \t]+(\d+\.\d+\.\d+\.\d+)',trace_seq_post[i]).group(1)
                    if ip_pre != ip_post:
                        print_result('trace: same number of hops but different path','precheck result',output_pre_trace[key],'postcheck result',output_post_trace[key])
                        break
                        
if __name__ == '__main__':
    analyze_output_pre_and_post(sys.argv[1].split('.')[0])
    