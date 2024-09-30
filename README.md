# JIRA Time Logger

A tool for automated time logging in JIRA Tempo. 

Usage: 

Clone: git clone https://gitlab.gk.gk-software.com/mkhan/jira-time-logger

In Terminal/CMD: Go to the project's root directory.

Run following command: 

`python3 log_time.py path_to_input_file`

A Sample input file "sample_input_file.txt" is provided for guide on it's format

## Requirements
- python 3.8.10 or above

## Dependencies 
Following python packages are used (install with pip if not installed already):
```bash
sudo apt install --no-install-recommends python3-pip
pip install requests datetime jproperties
```

## Running via Docker
```bash
docker build --no-cache --tag=mkhan/jira-time-logger .
docker run -it --rm -v $(pwd):/usr/src/app mkhan/jira-time-logger python log_time.py diary.txt
```

## Help commands

### Print computer's turn on/off
```bash
zgrep -e "New seat seat0" -e "System is powering down" /var/log/auth.log*
```
On managed Linux:
```bash
docker run -it --rm -v /var/log:/logs ubuntu:latest bash
zgrep -e "New seat seat0" -e "System is powering down" /logs/auth.log*
```
Alternative commands:
```bash
last reboot
journalctl --list-boots
```