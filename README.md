# launcher
Python script to launch Windows CLI pogram that need access to USB ports for Xilinx 1525 FPGA cards.
The script will get a list of FPGA cards, lock them out by opening the corresponding COM port, and release the ports one by one while running Window CLI instances that talk to the FPGA cards.

8 Apr 2019:>br>
The script can program partial bitstreams by adding them in a batch file

---- Sample batch file for partial bitstreams ----
cd c:\users\xxxx\desktop\bitstreams
launch.py -b bs_top.bit
launch.py -b bs0.bit
launch.py -b bs1.bit
launch.py -b bs2.bit
launch.py -b bs3.bit
.....
launch.py -b bsn.bit
---- end of sample ----

30 Dec 2018:<br>
Script now can program bitstreams to cards without running Vivado<br>
Use option -b<br>
<b>python launch.py -b c:\users\hashm1n3r\Desktop\BS\bitstream.bit</b><br>
A card database needs to be created once using option -i<br>
<b>python launch.py -i</b><br>
The cards are programmed sequentially, and require a working installation of Vivado Lab.<br>
The script uses the xsdb binary from Vivado to program the cards. There is still the time delay when Vivado hardware manager
tries to scan for all cards in a system.<br>
It is recommended to open Vivado and leave the hardware manager in Auto-detect before running the script, with the cards detected by Vivado. This avoid re-scanning of FPGA cards each time the script starts<br>

# instructions

Install Python 3.7 for Windows<br>
https://www.python.org/downloads/windows/<br>

Download the "Windows x86-64 executable installer" version
Ensure "Add Python 3.7 to PATH" Option is selected on the installer<br>

From a Command Prompt, install the pywin32 and pyserial modules:<br>

<b>
pip install pypiwin32<br>
pip install pyserial<br>
</b>

Edit and change the <b>working_dir</b> and <b>cmd</b> variables at the start of the script to suit your environment.<br>
<b>cmd</b> should be the name of the .cmd or .bat file to launch the CLI program<br>

Note the double backslashes "\\\\" used to escape "\\\" in windows path<br>
working_dir = "C:\\\\Users\\\\hashm1n3r\\\\Desktop";

You wil need to stop all the instances of the windows program that tries to access the FPGAs.<br>
THe script will relaunch them all<br>

You can execute a different program for each card. This is configured at the beginning of the script:

custom_cmd = {<br>
        "2143028XXX03C" : "nh_530.cmd",<br>
        "1280962XXX02C" : "nh_510.cmd",<br>
        "214302895XXXC" : "nh_510.cmd",<br>
        "dummy"         : "dummy"<br>
        }<br>
        
In this case these cards are run at different clock rates.<br>
All other cards run the default program specified in <b>cmd</b> variable<br>

You can also use custom command to run different miners.<br>
 
Example:<br>

C:\Users\hashm1n3r\>python launch.py<br>
COM4 2143028XXX03C<br>
COM5 1280962XXX02C<br>

Locking out card  2143028XXX03C by opening Serial Port COM4<br>
Locking out card  1280962XXX02C by opening Serial Port COM5<br>

Unlocking card 2143028XXX03C by closing serial port COM4<br>
Starting CMD for card 2143028XXX03C on COM4<br>
Unlocking card 1280962XXX02C by closing serial port COM5<br>
Starting CMD for card 1280962XXX02C on COM5<br>

Starting CMD for card 2143028XXX03C on COM4: nh_530.cmd<br>
Starting CMD for card 1280962XXX02C on COM5: nh_510.cmd<br>
C:\Users\hashm1n3r\><br>


Remember to disable MS serial mouse detection<br>
If you don't, some serial port might be claimed by MS as MS Serial Ballpoint Mouse
http://www.taltech.com/support/entry/windows_2000_nt_serial_mice_and_missing_com_port<br>

<li>Click on the Windows start button
<li>In the search box, type in: regedit and press the enter key on your keyboard
<li>The Registry editor windows will open
<li>Navigate to the registry key named: HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\sermouse
<li>On the right hand side of the registry editor window you should find subkey named: start
<li>Double click on the "start" subkey and modify the value of the key to: 4 and click the OK button to return to the registry editor window
<li>Note: setting the "start" subkey value to 4 will disable windows from looking for serial mice at startup
<li>Exit the regitstry editor window and reboot
