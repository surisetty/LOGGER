#!/bin/bash 


# This script will pull the latest code from the repo, 
# ./update.sh to update the code on the device. 
# Device should be connected to internet 



#  remove previous instances if any 
rm -f master.zip* 
rm -rf LOGGER-master 

# pull latest maste repo code
wget https://github.com/surisetty/LOGGER/archive/master.zip

#extract new code 
if [ -f master.zip ]; then 
   echo "Extracting new code" 
   unzip master.zip
   rm -f master.zip # remove zip file 
else 
   echo "Update file not found" 
   exit 1 
fi

#  find and remove all the previous application files. 
ls -l | egrep -v "LOGGER-master|master.zip|update.sh" | awk '{print $9}'  | xargs  rm -rf {}\;

# move new code to current dir and remove extracted folder 
mv LOGGER-master/* .
rm -rf LOGGER-master


