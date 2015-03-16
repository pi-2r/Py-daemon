#!/usr/bin/env python
#-*- coding: utf-8 -*-

import smtplib
import psutil
import sys
import os
import optparse
import time

from daemon import runner
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Class that contains all the toolbox
class Tools(object):

    def __init__(self, see_pid):
        """
        Constructor of the toolbox:
            contains the PID and the psutil object.

        :arg see_pid: PID to monitor.
        """
        self._pid = None
        self._see_pid = see_pid
        self._p = psutil

    def check_pid(self):
        """
        Check if the pid exist.
        If the PID doesn't exist for any reason, the program ends.
        """
        try:
            if psutil.pid_exists(self._see_pid):
                    self._pid = psutil.Process(self._see_pid)
                    return 1
            else:
                    print "[Error] This PID doesn't exist"
                    sys.exit(0)
        except psutil.NoSuchProcess as err:
            sys.exit(str(err))

    def convert_bytes(self, number):
        '''
        Method that converts the bytes in the correct format.

        :arg number: the number of bytes.  
        '''
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if number >= prefix[s]:
                value = float(number) / prefix[s]
                return '%.1f%s' % (value, s)
        return "%sB" % number

    def nb_files_descriptors(self):
        """
        Return all the number off file descriptors
        """
        return self._pid.num_fds()
            
            
    def m_virtual_memory(self):
        '''
        Dump memory usage of server: virtual memory
        '''
        mem = self._p.virtual_memory()
        # print "psutil: total=%s used=%s free=%s\n" % (mem.total / 1048576, mem.used / 1048576, mem.free / 1048576)
        return "virtual memory: total=%s available=%s free=%s percent=%s used=%s active=%s inactive=%s buffers=%s  cached=%s" % (self.convert_bytes(mem.total), self.convert_bytes(mem.available), self.convert_bytes(mem.free), mem.percent, self.convert_bytes(mem.used), self.convert_bytes(mem.active), self.convert_bytes(mem.inactive), self.convert_bytes(mem.buffers), self.convert_bytes(mem.cached))
        
    def m_swap_memory(self):
        '''
        Dump memory usage of server: swap memory
        '''
        swap = self._p.swap_memory()
        return "swap memory: total=%s used=%s free=%s percent=%s sin=%s sout=%s" % (self.convert_bytes(swap.total), self.convert_bytes(swap.used), self.convert_bytes(swap.free), swap.percent, self.convert_bytes(swap.sin), self.convert_bytes(swap.sout))

    def m_usage_deamon(self):
        '''
        Dump memory usage of daemon
        '''
        mud = self._pid.memory_info()
        return "Dump memory usage of daemon: resident=%s virtual=%s" % (self.convert_bytes(mud.rss), self.convert_bytes(mud.vms))

    def load_average(self):
        '''
        Return the load average.
        http://www.howtogeek.com/howto/ubuntu/get-cpu-system-load-average-on-ubuntu-linux/
        '''
        return "Load Average: ", os.getloadavg()

    def all_fd(self):
        '''
        All opened file descriptor
        linux commande:  os.system("ls -l /proc/"+ str(self._see_pid) +"/fd/")
        '''
        string = None
        all_fd = self._pid.open_files()
        for element in all_fd:
           string += str(element) + "\n"
        return string
        

    def get_coredump(self):
        '''
        http://stackoverflow.com/questions/141802/how-do-i-dump-an-entire-python-process-for-later-debugging-inspection
        '''
        return "todo"



#Class that send e-mail with your Google account
class  SendMail(object):

    def __init__(self, password, email, smtp, port):
        """"
        Constructor:
            contains all the information about the
            password, the original mail address of the SMTP
            and the port.

        :arg password: mailbox password.
        :arg email: email.
        :arg smtp: stmp server.
        :arg port: port.
        """
        self.msg = MIMEMultipart()
        self._password = password
        self._email = email
        self._smtp = smtp
        self._port = port


    def send_email(self, from_user, to, subject, message):
        """
        Method for sending one email.

        :arg from_user: adresse mail de l'envoyer.
        :arg to: adresse mail du destinataire.
        :arg subject: sujet du mail.
        :arg message: corps du message.
        """

        self.msg['From'] = from_user
        self.msg['To'] =  to
        self.msg['Subject'] = subject
        self.message = message
        self.msg.attach(MIMEText(self.message))
        mailserver = smtplib.SMTP(self._smtp, self._port)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login(self._email, self._password)
        mailserver.sendmail(from_user, to, self.msg.as_string())
        mailserver.quit()
   
#Class that launch a deamon in order to monitor a PID
class Monitoring(object):

    def __init__(self, pid):
        '''
        Constructor:
            contains all stdin/stdout/stderr path,
            the path where the PID deamon will be stored,
            and the call at the other class.

        :arg pid: PID.
        '''
        self.pid_name = 'my_monitoring.pid'
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/'+self.pid_name
        self.limit_fd = 1
        self.sleep_time = 10
        self.pidfile_timeout = 5
        self.see_pid = pid
        self.tools = Tools(self.see_pid)
        self.mail = SendMail("$password", "$email", "smtp.gmail.com", "587")
        self.message = None


    def  check_pid_from_monitoring(self):
    	'''
    	Method that checks if the PID exist
    	'''
    	try:
    		self.tools.check_pid()
    	except Exception, e:
            print "[Error]: ", e
            sys.exit(0)

    def start_notify(self):
        '''
        Method that notify by mail the beginning of the monitoring.
        '''
        #We read the PID of py-daemon
        file = open(self.pidfile_path, 'r')
        self.message = "Deamon PID: " + file.read()
        self.mail.send_email("localhost", "$your_email", "[my_monitoring] Start Monitoring", self.message)
        self.message = None

    def alert_notify(self):
        '''
        Method that notify by mail the alert of the monitoring.
        '''
        self.message = "PID to be monitored.: " + str(self.see_pid)
        self.message += "\n-Number of FD: " + str(self.tools.nb_files_descriptors())
        self.message += "\n-" + str(self.tools.m_virtual_memory())
        self.message += "\n-" + str(self.tools.m_swap_memory())
        self.message += "\n-" + str(self.tools.m_usage_deamon())
        self.message += "\n-" + str(self.tools.load_average())
        self.message += "\n-" + str(self.tools.all_fd())
        self.mail.send_email("localhost", "$your_email", "[my_monitoring] Alert", self.message)
        self.message = None

    def error_notify(self, error):
        '''
        Method that notify by mail the alert of the monitoring.

        :arg error: error message.
        '''
        self.mail.send_email("localhost", "$your_email", "[my_monitoring] Monitoring Error", str(error))
        self.message = None


    def run(self):
        '''
        Main method that monitor the PID
        '''

        self.start_notify()

        try:
            while True:
            	self.check_pid_from_monitoring()

                if self.limit_fd < self.tools.nb_files_descriptors:
                    self.alert_notify()
                
                time.sleep(self.sleep_time)

        except Exception, e:
            self.message = "[Error]: ", e
            self.error_notify(self.message)
            sys.exit(0)

# Main 
if __name__=='__main__':

    # Check if the programme can read and write in the tmp folder
    ret = os.access("/tmp/", os.R_OK)
    ret2 = os.access("/tmp/", os.W_OK)
    if ret and ret2:
        parser = optparse.OptionParser('[-] Use Help or "-help" for more information')
        # all the option are definided here
        parser2 = optparse.OptionParser(' %prog '+' <start/stop> -p <deamon PID>')
        parser2.add_option('-p', dest='pid', type='int',  help='specify the daemon pid')
        (options, args) = parser2.parse_args()
        pid = options.pid

        # check all the condition before start the deamon
        if ((pid == None)):
            print parser.usage
            exit(0)
        elif ((pid == 'help') or (pid == 'Help') or (pid == 'h') or (pid == None) or pid < 0):
            print parser2.usage
            exit(0)
        elif ((pid != None) and pid > 0):
            momitoring = Monitoring(pid)
            momitoring.check_pid_from_monitoring()
            daemon = runner.DaemonRunner(momitoring)
            daemon.do_action()
    else:
        print "[Error] Please to check the read/write permissions of 'tmp' folder"
        sys.exit(0)
