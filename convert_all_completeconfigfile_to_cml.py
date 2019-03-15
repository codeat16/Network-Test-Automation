from subprocess import call

allconfigfiles = [
	'r1.txt',
	'r2.txt',
	'r3.txt',
	'r4.txt',
	'r5.txt',
	'r6.txt',
	'r7.txt',
	'r8.txt',

	'r9.txt',
	'r10.txt',
	'r11.txt',
	'r12.txt',
	'r13.txt',
	'r14.txt',
	'r15.txt',
	'r16.txt',
	'r17.txt',
	'r18.txt',
	'r19.txt',
	'r20.txt'
	]

for file in allconfigfiles:
    cmd1=["python","convert_completeconfigfile_to_cml.py"]+[file]
    print( cmd1 )
    call( cmd1 )
    
    ''' The del command failed in Windows: FileNotFoundError: [WinError 2] The system cannot find the file specified
    cmd2=["del"]+[file]
    print( cmd2 ) 
    call( cmd2 )
    '''
    