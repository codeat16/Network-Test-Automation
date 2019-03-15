import paramiko
import telnetlib
import time
import unittest

SSH_WAIT_TIME = 2
TELNET_WAIT_TIME = 2
TESTIP1 = '10.1.1.100'
TESTIP2 = '10.1.1.200'
USER1 = 'user1'
PASS1 = 'pass1'
USER2 = 'user2'
PASS2 = 'pass2'

pre1 = '!---'
post1 = '---!'
pre2 = '!-----'
post2 = '-----!'

class CliConn(object):
    ''' CLI object for high level command for ssh or telnet shell
    Methods:
        init(): read the essential ip, port, user, pass, etc.
        open(): open the CLI, login, set terminal length to 0 to be ready for next command
        close(): close connect 
        cmd(): main interaction with the CLI
    '''
    def __init__(self,ip=None,username=None,password=None,port=None,termtype='telnet',outputfile=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.termtype = termtype
        self.IsOpen = False
        self.term = None
        self.termshell = None
        self.debug = False
        self.outputfile = outputfile
    
    
    def open(self):
        if self.debug:
            print(pre1 + 'Executing open({})'.format(str(self)) + post1 )
            if self.outputfile:
                self.outputfile.write(pre1 + 'Executing open({})'.format(str(self)) + post1 +'\n')
            
        if self.termtype == 'ssh':
            self.term = paramiko.SSHClient()
            self.term.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.term.connect(
                hostname = self.ip,
                port = self.port,
                username = self.username,
                password = self.password,
                )
            self.termshell = self.term.invoke_shell()
            # set term length 0 and flush buffer
            self.termshell.recv(5000)
            self.termshell.send('ter len 0\n')
            time.sleep(SSH_WAIT_TIME)
            self.termshell.recv(5000)
            self.IsOpen = True
            
        elif self.termtype == 'telnet':
            self.term = telnetlib.Telnet(self.ip, self.port)
            #open() optinal. also works without open
            #self.term.open(self.ip, self.port, 7200)
            # \r is necessary to get the initial screen in CML and get Username: prompt
            result=self.term.write(b'\r\n')
            if self.debug:
                print(pre2 + 'write return newline: ()'.format(result) + post2)
                if self.outputfile:
                    self.outputfile.write(pre2 + 'write return newline: ()'.format(result) + post2 +'\n')
            # Either sleep or nonblocking wait is necessary to work around router's slow login protection
            # Experiment showed b'string' format match better then using str then encode to ascii
            #time.sleep(2)
            firstread = self.term.read_until(b'Username: |#', TELNET_WAIT_TIME).decode('ascii')
            if self.debug:
                print(pre2 + 'read_until(Username: |#): {}'.format(firstread) + post2)
                if self.outputfile:
                    self.outputfile.write(pre2 + 'read_until(Username: |#): {}'.format(firstread) + post2 +'\n')
            if len(firstread) >= 1:
                if firstread[-1] == ' ':
                    self.term.write( (self.username + '\n').encode('ascii'))
                    self.term.read_until(b'Password: ', TELNET_WAIT_TIME)
                    self.term.write( (self.password + '\n').encode('ascii'))
                    self.term.read_until(b'#', TELNET_WAIT_TIME)
            result=self.term.write(b'ter len 0\n')
            if self.debug:
                print(pre2 + 'terl len 0: {}'.format(result) + post2)
                if self.outputfile:
                    self.outputfile.write(pre2 + 'terl len 0: {}'.format(result) + post2 +'\n')
            result=self.term.read_until(b'#', TELNET_WAIT_TIME)
            if self.debug:
                print(pre2 + 'read_until(#): {}'.format(result) + post2)
                if self.outputfile:
                    self.outputfile.write(pre2 + 'read_until(#): {}'.format(result) + post2 +'\n')
                
            self.IsOpen = True    
            
        else:
            raise            

            
    def close(self):
        if self.debug:
            print(pre1 + 'Executing close({})'.format(str(self)) + post1)
            if self.outputfile:
                self.outputfile.write(pre1 + 'Executing close({})'.format(str(self)) + post1 +'\n')
            
        if self.IsOpen:
            if self.termtype == 'ssh':
                self.termshell.close()
                self.term.close()
                self.IsOpen = False
            elif self.termtype == 'telnet':
                self.term.close()
                self.IsOpen = False
            else:
                raise
            
            
    def cmd(self,cmdstring):
        if self.debug:
            print(pre1 + 'Executing cmd({},{})'.format(str(self),cmdstring) + post1)
            if self.outputfile:
                self.outputfile.write(pre1 + 'Executing cmd({},{})'.format(str(self),cmdstring) + post1 +'\n')
            
        if cmdstring[-1] == '\n':
            cmd = cmdstring
        else:
            cmd = cmdstring+'\n'
        
        if not self.IsOpen:
            self.open()
        
        if self.termtype == 'ssh':
            if self.debug:
                print(pre2 + 'sending "{}" to ssh channel'.format(cmd) + post2)
                if self.outputfile:
                    self.outputfile.write(pre2 + 'sending "{}" to ssh channel'.format(cmd) + post2 +'\n')
            self.termshell.send(cmd)
            time.sleep(SSH_WAIT_TIME)
            rawresult = self.termshell.recv(5000)
            return rawresult.decode('utf-8')
          
        elif self.termtype == 'telnet':
            if self.debug:
                print(pre2 + '----sending "{}" to telnet channel----'.format(cmd) + post2)
                if self.outputfile:
                    self.outputfile.write(pre2 + '----sending "{}" to telnet channel----'.format(cmd) + post2 +'\n')
            self.term.write(cmd.encode('ascii'))
            if cmd.startswith('trace'):
                # 2 seconds timeout, 2 probe per hop, 5 hop allowance
                rawresult = self.term.read_until(b'#', 30)
            else:
                rawresult = self.term.read_until(b'#', TELNET_WAIT_TIME)
            return rawresult.decode('ascii')
            
        else:
            raise

            
class TestCliConn(unittest.TestCase):            
    def test_ssh(self):
        ssh = CliConn(ip=TESTIP1,username=USER1,password=PASS1,port=22,termtype='ssh')
        ssh.debug = True
        print(pre1 + 'CliConn ojected created: {} '.format(str(ssh)) + post1)
        
        ssh.open()
        print(pre1 + 'open() exected' + post1)
        
        result = ssh.cmd ('ls')
        print(pre1 + 'cmd(ls) executed. Result follows: ' + post1)
        print(result)
        
        print(pre1 + 'Press enter to send 2nd command' + post1)
        input()
        
        result = ssh.cmd ('ls -al')
        print(pre1+ 'cmd(ls -al) executed. Result follows: ' + post1)
        print(result)
        
        print(pre1 + 'Press enter to send 3rd command' + post1)
        input()
        result = ssh.cmd ('ls -alR')
        print(pre1 + 'cmd(ls -alR) executed. Result follows: ' + post1)
        print(result)   
        #Once closed, cannot be reopen for Paramiko        
        ssh.close()

        
    def test_ssh_autoopen(self):
        print(pre1 + 'Press enter for auto open' + post1)
        input()    
        ssh = CliConn(ip=TESTIP1,username=USER1,password=PASS1,port=22,termtype='ssh')
        ssh.debug = True
        print(pre1 + 'CliConn ojected created: {} '.format(str(ssh)) + post1)
         
        result = ssh.cmd ('ls')
        print(pre1 + 'cmd(ls) executed. Result follows: ' + post1)
        print(result)

        ssh.close()

        
    def test_telnet(self):
        telnet = CliConn(ip=TESTIP2,username=USER2,password=PASS2,port=17117,termtype='telnet')
        telnet.debug = True
        print(pre1 + 'CliConn ojected created: {} '.format(str(telnet)) + post1)
        
        telnet.open()
        print(pre1 + 'open() exected' + post1)
        
        result = telnet.cmd ('sh ip int brief')
        print(pre1 + 'cmd(sh ip int brief) executed. Result follows: ' + post1)
        print(result)
        
        print(pre1 + 'Press enter to send 2nd command' + post1)
        input()
        
        result = telnet.cmd ('sh log | in CDP')
        print(pre1 + 'cmd(sh log | in CDP) executed. Result follows: ' + post1)
        print(result)
        
      
        print(pre1 + 'Press enter to send 3rd command' + post1)
        input()
        result = telnet.cmd ('sh ip ospf int brief')
        print(pre1 + 'cmd(sh ip ospf int brief) executed. Result follows: ' + post1)
        print(result)        
        telnet.close()

        
    def test_telnet_autoopen(self):
        print(pre1 + 'Press enter for auto open' + post1)
        input()    
        telnet = CliConn(ip=TESTIP2,username=USER2,password=PASS2,port=17117,termtype='telnet')
        telnet.debug = True
        print(pre1 + 'CliConn ojected created: {} '.format(str(telnet)) + post1)
         
        result = telnet.cmd ('sh int')
        print(pre1 + 'cmd(sh int) executed. Result follows: ' + post1)
        print(result)

        telnet.close()
        
        
if __name__ == '__main__':
    unittest.main()
    #test = TestCliConn()
    #test.test_telnet()
    #test.test_telnet_autoopen()    