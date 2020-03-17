from time import sleep
from threading import Thread

import os
import collections
import thread
from Queue import Queue

import paramiko
from getpass import getpass
import time

print "Modules are imported successfully"



class deviceCommand():
    def __init__(self, command, waitingTimeToGetOutput = 5):
        self.command = command
        self.commandOutput = "unset"
        self.waitingTimeToGetOutput = waitingTimeToGetOutput



class Device:
    def __init__(self,ip, username, password, infiniteOutputKeyword = "terminal length 0"):
        self.ip = ip
        self.username = username
        self.password = password
        self.processSteps = 0
        self.connection = 0
        self.infiniteOutputCommand = infiniteOutputKeyword
        self.commandsToGetIn = []

            
    def getMeViaSSH(self):
            try:
                remote_conn_pre=paramiko.SSHClient()
                remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                remote_conn_pre.connect(self.ip, port=22, username=self.username, password=self.password,look_for_keys=False, allow_agent=False)
                remote_conn = remote_conn_pre.invoke_shell()
                output = remote_conn.recv(65535)
                self.connection = 1
                        
                self.processSteps = 1
                print(self.ip + " step 1")
                remote_conn.send("term len 0" + "\n")
                time.sleep(5)
                self.hostname = remote_conn.recv(65535).rsplit('\n')[1].split('#')[0]

                self.processSteps = 2
                print(self.ip +" step 2")
                for work in self.commandsToGetIn:
                    remote_conn.send(work.command + "\n")
                    time.sleep(work.waitingTimeToGetOutput)
                    work.commandOutput = remote_conn.recv(65535)

            except Exception, e:
                if not self.connection:
                    print self.ip + " not reachable"
                if not self.processSteps:
                    print self.ip + " process failed at step of " + str(self.processSteps)
            finally:
                if remote_conn_pre:
                    remote_conn_pre.close()       
                    print self.ip + "done"


orderOfDevices = Queue()


def deviceHandler(que):
    while True:
        node = que.get()
        node.getMeViaSSH()
        que.task_done()


if __name__ == "__main__":
    startingTime = time.time()
    devices = []

    tempDevice = Device("1.1.1.1", "USERNAME1", "PASSWORD1")
    commands = [deviceCommand("show int desc") , deviceCommand("show ver"), deviceCommand("show int status")]
    tempDevice.commandsToGetIn = commands
    devices.append(tempDevice)
    del tempDevice

    tempDevice = Device("2.2.2.2", "USERNAME2", "PASSWORD2")
    commands = [deviceCommand("show int desc") , deviceCommand("show ver"), deviceCommand("show int status")]
    tempDevice.commandsToGetIn = commands
    devices.append(tempDevice)
    del tempDevice


    tempDevice = Device("3.3.3.3", "USERNAME3", "PASSWORD4")
    commands = [deviceCommand("show int desc") , deviceCommand("show ver"), deviceCommand("show int status")]
    tempDevice.commandsToGetIn = commands
    devices.append(tempDevice)
    del tempDevice


    tempDevice = Device("4.4.4.4", "USERNAME4", "PASSWORD4")
    commands = [deviceCommand("show int desc") , deviceCommand("show ver"), deviceCommand("show int status")]
    tempDevice.commandsToGetIn = commands
    devices.append(tempDevice)
    del tempDevice


    print "Threads loading..."
    for i in range(10):
        t = Thread(target = deviceHandler, args = (orderOfDevices,))
        t.daemon = True
        t.start()
    print "Threads online..."
    #Adding devices a que
    for node in devices:
        orderOfDevices.put(node)

    #Waiting for an empty que
    orderOfDevices.join()

    print "Process takes %s seconds to complete" % (time.time() - startingTime)
    print "Result*************************************************"
                
    for device in devices:
        if device.connection:
            print "Outputs of commands for device with ip of " + device.ip
            for command in device.commandsToGetIn:
                print "Command: \n" + command.command
                print "Output: \n" + command.commandOutput
                
    print "Process can be reported as finished, but please check output of 'ps -lf' on linux, and task manager on windows to check any unwanted thread lasting to work."