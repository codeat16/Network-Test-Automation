# Network Change Test Automation

This is a module for automated testing of network changes. It is for demo purpose only as the environment for it to run is very specific and might not be for everyone.

## Environment

The setup environment is for a very specific network and endpoints consisnt of above 80 simulated devices. The type of simulated devices include IOS-XR&trade;, IOS&trade;, and Ubuntu devices simulated using Cisco Modeling Lab&trade;. Cisco Model Lab&trade; and the network device OS such as IOS-XR&trade;, IOS&trade; are licensed software by Cisco Systems, Inc. and are not part of the provision.

## Methodology

A specific network and endpoints are built inside CML. The endpoints are used for connectivity test of the network. This serves as the simulation model of the network. Then user create a script file for desired configuration change to the network. The script file consists of CLI commands and is just like a normal script file a network engineer will use to configure a network device through CLI. Some simple directives allow to specify multiple devices in the script file and allow for multiple stage commits.

This repo will then read the script file, apply to all network devices per the order, and then at each checkpoint (of commit), perform any to any connectivity test using Ping and Traceroute.

The test result are further parsed to provide simplied report for a simple pass or pointed out the problematic area. The deviation of connectivy test result before change and after change are compared and with difference reproted. Connectivity loss and path change are detected and reported. The path change can be used as a approximate for the latency change of the network path when the exact latency is not easily simualted precisely in this software based simulation environment.



# Usage

The flow of automated testing consists of the following steps:

1. User build an aggregate config file for the command to change the network. The config file are originary CLI command to be enter into the network, starting with "conf t", and "commit". The config file also include @routerhostname directive to tell which router the command should be performed. It is user's responsibility to put proper commit through the step. One config file is considered one change, and one change can have config commands for multiple routers.

2. This tool parses the config file. Then it performs the following:
 a. A pre-change any to any connectivity test using Ping and Traceroute. Collected the output to identify the connecitivy and the network path taken from any A to Z combination.
 b. Execute the CLI commands in the script to the specified network devices. Once all scripts have been executed, a post-change any to any connectivity test is performed again. User can opt for a checkpoint to perform connectivity test at any "commit" command, or only one checkpoint at the end of the script file.

3. The pre, post change test results are compared and with different reported. A report with no difference is considered a pass as the change does not affect connecitivy of network in any way. Any difference will be reported and user can judge whether the differences are acceptable.


# Further consideration

A multi-thread version of the tool was attempted to speed up the execution of the connectivity test. However, it was found that the underlying simulation environment (CML), given that the entry point is single thread, is not multiple ready and that cause unexpected and potentially incorrect result.


# Files list

- __cliconn.py__ : Module to provide ssh/telnet interaction to network devices.
- __cml_interface_map.json__ : Mapping of interface numbering from actual production numbering to simulation numberings.
- __convert_all_completeconfigfile_to_cml.py__ : Conversion of a group of config files into simuation compatible format.
- __convert_completeconfigfile_to_cml.py__ : Convert one complete network config file into applicable simulation format with translated interface numberings and with hardware specific commands removed.
- __convert_config_to_cml.py__ : Convert user created script file into simulation format with translated interface numberings.
- __diff-cml.py__ : diff two config files after removing the hardware specific commands and are in comparable, simualtion ready format.
- __exec_change v4.py__ : The main auto testing module that go through pre-test, execute config commands to network devices, and do post-test.
- __exec_change_1addname_to_output.py__ : Post processing of adding readable hostname to test report.
- __exec_change_2compare_pre_post.py__ : Post processing of comparing pre-test results to post-test results.
- __exec_change_3analyze_pre_post.py__ : Logic to filter uninterested results and attempt to present only relevant results.
- __exec_change_mt.py__ : Multithread version of the main auto testing module.
- __parse_virl_to_config_files.py__ : Extact from a simulation config file that include all network devices to separate config files for each devices.
- __parse_virl_to_ipnamemapping.py__ : Extact from a simulation config file the hostname to management ip addres mapping.

