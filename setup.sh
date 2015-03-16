#!/bin/bash
name_program="monitoring.py"
email="Google email"
password="Google password"
your_email="your_mail"


if [[ $EUID -ne 0 ]]; then
   echo -e "\033[31m[-] This script must be run as root. \033[0m"
   exit 1
fi

if [ -f $name_program ]
then
   echo -e "\033[32m[+] The python program existe. \033[0m"
else 
	echo -e "\033[31m[-] The python program not exist. \033[0m"
   	exit 1
fi

var=$(pwd)

function sedeasy {
  sed -i "s/$(echo $1 | sed -e 's/\([[\/.*]\|\]\)/\\&/g')/$(echo $2 | sed -e 's/[\/&]/\\&/g')/g" $3
}

echo -e "\033[32m[+] Debian Update \033[0m"
apt-get update 

echo -e "\033[32m[+] Installation of the following packages: python-dev, python-pip, python-daemon, psutil \033[0m"
apt-get install -y python-dev python-pip python-daemon 

pip install psutil


echo -e "\033[32m[+] Configuration of your monitore \033[0m"
sedeasy '$email' ''$email'' $var"/"$name_program
sedeasy '$password' ''$password'' $var"/"$name_program
sedeasy '$your_email' ''$your_email'' $var"/"$name_program

echo -e "\033[32m[+] You can launch the python program (python monitoring.py -h) \033[0m"
