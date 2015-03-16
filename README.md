# Py-daemon
 Small program in python that monitor a specific daemon by its PID, and that sends alert emails.
 
 How to:
-----------

Step1:
In the setup.sh, you need to change the default configuration.
You need to change this variables:

 		email="Google email"
		password="Google password"
		your_email="your_mail"

by your own identifiers.
 
 Step2: 
 Change the chmod of this script, in order to make it executable (chmod +x setup.sh)
 
 Step3: 
 You need to be root to execute the script.sh, in order to install python-dev, python-pip, python-daemon and psutil
 
 Step4: 
 Excute the python daemon with this commande: python monitoring.py -h
 
 Documentation :
--------------------
py-deamon:  https://pypi.python.org/pypi/pydaemon

psutil: http://pythonhosted.org/psutil/

argparse: https://docs.python.org/3/library/argparse.html
