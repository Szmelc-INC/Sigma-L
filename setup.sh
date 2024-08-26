#!/bin/bash

clear

echo "SigmaL Setup Wizard"
sleep 1.5

# Check if Python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install Python3."
    exit
fi

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null
then
    echo "pip3 could not be found. Installing pip3..."
    sudo apt-get update
    sudo apt-get install python3-pip -y
fi

# Check if netcat (nc) is installed
if ! command -v nc &> /dev/null
then
    echo "Netcat (nc) could not be found. Installing netcat..."
    sudo apt-get update
    sudo apt-get install netcat -y
fi

# Check if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found. Installing jq..."
    sudo apt-get update
    sudo apt-get install jq -y
fi

# Install Python requirements
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Setup completed successfully."
sleep 1
clear 
echo "Run python3 main.py to start SigmaL"

# Assume something had been installed and proceed to cleanup lol
rm setup.sh requirements.txt

sleep 2

python3 main.py &
