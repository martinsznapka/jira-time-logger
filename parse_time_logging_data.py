import date_time_utils
import jira_helper
from bcolors import BColors
import re

delimeter="|"

class JiraEntry:
	def to_dict(self):
		return {
		'issue_id': self.issue_id,
        'issue_date': str(self.issue_date),
        'start_time': str(self.start_time),
        'end_time': str(self.end_time),
        'description': self.description,
        'origin_task_id': self.origin_task_id
        }

	def __init__(self, issue_id, issue_date, start_time, end_time, description, origin_task_id):
		self.issue_id = issue_id
		self.issue_date = issue_date
		self.start_time = start_time
		self.end_time = end_time
		self.description = description
		self.origin_task_id = None # should be calculated later, so remove it from the constructor? 

	def set_origin_task_id(self, origin_task_id):
		self.origin_task_id=origin_task_id




def validate_time(time_span):
	time_range = time_span.split("-")
	if re.search("[0-2][0-9]\:[0-9][0-9]\-[0-2][0-9]\:[0-9][0-9]", time_span) is None: # hh:mm-hh:mm
		return (False, "time range has a problem. Note: required format: hh:mm-hh:mm. provided time: "+str(time_span));
	is_time_range_valid, message = date_time_utils.validate_time_range(start_time=time_range[0], end_time=time_range[1])
	if(not is_time_range_valid):
		return (False, "time range has a problem: "+str(message))
	return (True, "time is valid")

def validate_jira_entry(line):
	issue_data = line.split(delimeter)
	if len(issue_data)!=3:
		return (False, "Data incomplete, required elements 3, provided elements "+str(len(issue_data)))
	if(len(issue_data[0].strip())<=0):
		return (False, "Issue Id is missing")
	if(len(issue_data[2].strip())<=0):
		return (False, "Work description is missing")
	is_time_valid, message = validate_time(issue_data[1].strip())
	if(not is_time_valid):
		return (False, str(message))
	return (True, "issue date is valid")

def show_help():
	print("\n\nGuide for adding a line:")
	print("\nA line must be in following format: ["+BColors.OKGREEN+"Issue-Id "+delimeter+" starttime-endtime "+delimeter+" description"+BColors.ENDC+"], format for starttime/endtime: hh:mm")
	print("\nExample:\t PMCA-1234 "+delimeter+" 09:55-10:15 "+delimeter+" mca daily\n")


def get_jira_entry(line, startDate):
	issue_data = line.split(delimeter)
	issue_id = issue_data[0].strip()
	time_range = issue_data[1].strip().split("-")
	description = issue_data[2].strip()
	return JiraEntry(issue_id, issue_date=startDate, start_time=date_time_utils.get_time_obj(time_range[0]), end_time=date_time_utils.get_time_obj(time_range[1]), description=description, origin_task_id="None")
	
def get_time_logging_data(file_name):
	with open(file_name) as f:
		lines = f.readlines()
	jira_entries = []
	startDate = None
	for line in lines:
		line = line.strip()
		if len(line)<=0 or line.startswith("Jira-Id") or line.startswith('#'): # ignore the empty line, or header, or comment,
			continue
		if line.startswith("Date:"): #select the date on which time is to be logged
			if len(line.split(":"))!=2:
				print("please provide start date in a format = Date: dd/mm/yy")
				exit(0)
			startDate = date_time_utils.get_date_obj(line.split(":")[1].strip())
			continue
		is_jira_entry_valid, message =validate_jira_entry(line)
		if not is_jira_entry_valid:
			print(BColors.HEADER+"Syntax Error in line: "+BColors.ENDC+"[" +BColors.FAIL+ str(line) +BColors.ENDC+"]."+" Root Cause: "+BColors.BOLD+str(message)+BColors.ENDC)
			show_help()
			exit(0)
			
		jira_entries.append(get_jira_entry(line, startDate))

	return jira_entries


def summarize_time_work_log(jira_entries):
	data_by_date = {}

	for jira_entry in jira_entries:
		if str(jira_entry.issue_date) in data_by_date:
			data_by_date[str(jira_entry.issue_date)] = data_by_date[str(jira_entry.issue_date)]+date_time_utils.get_time_elapsed_in_seconds(jira_entry.start_time, jira_entry.end_time)
		else:
			data_by_date[str(jira_entry.issue_date)] = date_time_utils.get_time_elapsed_in_seconds(jira_entry.start_time, jira_entry.end_time)
	return data_by_date

def fill_in_origin_task_id(jira_entries, j_session_id):
	origin_task_id_map = {}
	for jira_entry in jira_entries:
		if jira_entry.issue_id in origin_task_id_map:
			jira_entry.set_origin_task_id(origin_task_id_map[jira_entry.issue_id])
			continue
		task_origin_id, message = jira_helper.get_origin_task_id(jira_entry.issue_id, j_session_id)
		if task_origin_id==0:
			print("Error in getting taskOriginId for Issue: "+str(jira_entry.issue_id))
			print(message)
			exit(0)
		else:
			jira_entry.set_origin_task_id(task_origin_id)
			origin_task_id_map[jira_entry.issue_id]=task_origin_id
