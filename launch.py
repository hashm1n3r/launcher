#! python
import win32com.client;
import re;
import serial;
import time;
import os;
import sys;
import optparse;
from pathlib import Path
from subprocess import Popen, PIPE
import json


working_dir = "C:\\Users\\hashm1n3r\\Desktop\\BS";

cmd = "nh_520.cmd";

# add customised setting here
# format is "CARD SN" : "programm to run"
custom_cmd = {
        "1280962XXX51C" : "nh_530.cmd",
        "1280962XXX36C" : "nh_530.cmd",
        "2143028XXX2RC" : "nh_500.cmd",
        "2143028XXX25C" : "nh_500.cmd",
        "dummy"         : "dummy"
        }

xsdb = r"C:\Xilinx\Vivado_Lab\2018.2\bin\xsdb";
hw_server = r"C:\Xilinx\Vivado_Lab\2018.2\bin\hw_server.bat";
f = Path(xsdb);
if f.is_file() == False:
    print("XSDB binary File " + xsdb + " not found, please check.");
    exit();


parser = optparse.OptionParser();
parser.add_option('-b', '--bitstream', action="store", dest="bitstream", help="bitstream to program", default="none");
parser.add_option('-i', '--init', action="store_true", dest="init", help="initialise card database", default=False);
parser.add_option('-t', '--test', action="store_true", dest="test", help="Only list the cards", default=False);
parser.add_option('-v', '--verbose', action="store_true", dest="verbose", help="Print additional info", default=False);
parser.add_option('-c', '--command', action="store", dest="command", help="Default command for the cards", default="none");

options, args = parser.parse_args()

cards = {};
fds = {};
jtags = [];
instances = [];
count = 1;
tcp_port = 4000;

def get_usb_instances():
    "funtion to find a list of instance IDs corresponding to USB port"
    # Not currently used
    cmd = "devcon.exe find usb*";
    s = Popen(cmd, shell=True, stdout=PIPE).stdout
    lines = s.readlines()

    for l in lines:
        line = l.decode();
        m = re.search('(USB[0-9a-zA-Z\&\\\_]+).+USB Serial Converter A', line);
        if m:
            instance = m.group(1);
            instances.append(instance);
            print(instance);


def prog_bitstream(card, bitstream):
    "function to program bitstream to specified card"
    global tcp_port;

    tmp = bitstream.replace("\\", "\\\\");

    tcl = "connect\ntarget -set -filter {name == \"xcvu9p\" && jtag_cable_serial == \"" + card + "\"} -timeout 1\nfpga " + tmp + "\n";
    if options.verbose:
        print(tcl);
    print("Launching programmer for " + card + "...");
    global count;
    f = card + ".tcl";
    tcl_file = open(f, "w");
    tcl_file.write(tcl);
    tcl_file.close();
    cmd = xsdb + " " + f;
    if options.verbose:
        print(cmd)
    os.system(cmd);
    count = count + 1;
    tcp_port = tcp_port + 1;

def prog_bitstreams(bitstream):
    "funtion to find all cards and program them from INI"

    print("Reading card database from launch.ini...");
    try:
        file = open("launch.ini", "r");
    except:
        print("Problem reading launch.ini file.");
        print("Please create the card database with -i option");
        print("python launcher.py -i");
        exit();

    lines = file.readlines() 
    for card in lines:
        m = re.search('[0-9]', card);
        if m:
            jtags.append(card.rstrip());
            print(card.rstrip());

    print("Done, found " + str(len(jtags)) + " cards");


    for card in jtags:
        prog_bitstream(card, bitstream);
        time.sleep(1);


def write_ini():
    "funtion to write card info to INI file"

    print("Connecting to Vivado server...");
    print("Please wait, this could take a few minutes.");
    proc = Popen([xsdb, '-interactive'], shell=True, stdin=PIPE, stdout=PIPE)
    proc.stdin.write("connect\r\n".encode())
    time.sleep(1);
    proc.stdin.write("target -target-properties\r\n".encode())
    time.sleep(1);
    proc.stdin.write("exit\r\n".encode())
    output = proc.communicate()[0].decode();
    #print(output);

    regex = re.compile('\{')
    lines = regex.split(output)

    f = "launch.ini";
    ini_file = open(f, "w");

    tmp = {};
    for l in lines:
        m = re.search('jtag_cable_serial\s+([0-9a-zA-Z]+)', l);
        if m:
            card = m.group(1);
            tmp[card] = "dummy";

    for card, value in tmp.items():
            jtags.append(card);
            print(card);
            ini_file.write(card + "\n");


    ini_file.close();
    print("Done, found " + str(len(jtags)) + " cards");



def find_cards():
    "funtion to find all cards from Windows USB database"
    strComputer = ".";
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
    colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_PnPEntity")
    for objItem in colItems:
        m = re.search('PID_6011\+(.+C)\\\\', objItem.DeviceID);
        if m:
            sn = m.group(1)
            m = re.search('(COM\d+)', objItem.Name);
            if m:
                port = m.group(1);
                #print("Name:" + objItem.Name)
                #print("PORT:" + port);
                #print("DeviceID:" + objItem.DeviceID)
                print(port + " " + sn);
                cards[sn] = port;


if (options.init):
    write_ini();
    exit();

if (options.bitstream != "none"):
    f = Path(options.bitstream);
    if f.is_file():
        prog_bitstreams(options.bitstream);
    else:
        print("Bitstream " + options.bitstream + " not found, please check")
    exit();

if (options.command != "none"):
    cmd = options.command;
    f = Path(cmd);
    if f.is_file() == False:
        print("Command " + options.command + " not found, please check")
        exit();


find_cards();
if options.test:
    exit();

for key, value in cards.items():
    print("Locking out card  " + key + " by opening Serial Port "+ value)
    fds[key] = serial.Serial(value, 115200, timeout=0);

for key, value in cards.items():

    print("Unlocking card " + key + " by closing serial port " + value);
    fds[key].close();
    os.chdir(working_dir);
    if (custom_cmd.get(key)):
        print("Starting CMD for card " + key + " on " + value + ": " + custom_cmd.get(key));
        os.system("start " + custom_cmd.get(key));
    else:
        print("Starting CMD for card " + key + " on " + value + ": " + cmd);
        os.system("start " + cmd);
    time.sleep(30)

