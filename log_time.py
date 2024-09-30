import parse_time_logging_data as tl_parser
import date_time_utils
import jira_helper
import app_config
import progress_bar
import time
import getpass
import sys
from bcolors import BColors

if len(sys.argv)<2:
	print("Please provide the path to input file for reading time logging data")
	exit(0)

def build_report_line(jira_entry, status, details):
	return str(jira_entry.issue_id+report_delimeter+str(jira_entry.issue_date)+report_delimeter+
							  str(jira_entry.start_time)+report_delimeter+str(jira_entry.end_time)+report_delimeter+
							  status+report_delimeter+details+"\n")

def get_remaining_estimate_with_cache(jira_entry, j_session_id, remaining_estimate_cache):
	#look up in cache
	if jira_entry.issue_id in remaining_estimate_cache:
		remaining_estimate = remaining_estimate_cache[jira_entry.issue_id]
		#print("Jira["+str(jira_entry.issue_id)+"]"+"remaining_estimate from cache: "+str(remaining_estimate))
		if remaining_estimate == -1:
			remaining_estimate = "null"
		return remaining_estimate, "Success"
	# get it from jira
	for i in range(3):
		#print("get remaining estimate from jira for issue "+str(jira_entry.issue_id) + ", attempt: "+str(i))
		status, details, remaining_estimate, http_status_code = jira_helper.get_remaining_estimate(jira_entry, j_session_id)
		time.sleep(request_delay_seconds)
		if (status == "Failed"):
			report_line = build_report_line(jira_entry, status, details)
			continue #keep retrying for a few times until estimate is retrieved successfully
		#print("Got remaining estimate from Jira for issue["+str(jira_entry.issue_id)+"]: "+str(remaining_estimate))
		report_line = "Success"
		if remaining_estimate == -1:
			#print("Putting it in cache, key = "+str(jira_entry.issue_id)+", value = "+str(remaining_estimate))
			remaining_estimate_cache[jira_entry.issue_id]=remaining_estimate
			remaining_estimate = "null"
		if remaining_estimate == 0:
			#print("Putting it in cache, key = "+str(jira_entry.issue_id)+", value = "+str(remaining_estimate))
			remaining_estimate_cache[jira_entry.issue_id]=remaining_estimate

		#print("with_cache: returning remaining_estimate for jira["+str(jira_entry.issue_id)+"]: "+str(remaining_estimate))
		return remaining_estimate, "Success"

	return None, report_line


def do_log_time(run, jira_entries_to_log, j_session_id, remaining_estimate_cache):

	failed_work_log_lines = []
	failed_jira_o_entries = []
	with open('time_log_report_'+str(run)+'.tsv', 'w') as report_file:
		report_header = "Jira_Id"+report_delimeter+"Date"+report_delimeter+"Start Time"+report_delimeter+"End Time"+ \
						report_delimeter+"Status"+report_delimeter+"Details\n"
		report_file.write(report_header)
		failed_work_log_lines.append(report_header.replace("Jira_Id", "Jira_Id\t")
								.replace("Date", "Date\t")
								.replace("Status", "Status\t")) # some alignments for the console printing
		for i, jira_entry in enumerate(jira_entries_to_log):

			time.sleep(request_delay_seconds)
			progress_bar.printProgressBar(i, len(jira_entries_to_log), length = 50)
			remaining_estimate, report_line = get_remaining_estimate_with_cache(jira_entry, j_session_id, remaining_estimate_cache)
			if remaining_estimate is None:
				failed_work_log_lines.append(report_line.replace("Failed","Failed\t"))
				failed_jira_o_entries.append(jira_entry)
				report_file.write(report_line)
				continue
			status, details, http_status_code = jira_helper.log_time(jira_entry, remaining_estimate, j_session_id, owner_id)
			report_line = build_report_line(jira_entry, status, details)
			#TODO: repeat the time logs multiple times on failure without getting remaining estimate time from jira again
			if (status == "Failed"):
				failed_work_log_lines.append(report_line.replace("Failed","Failed\t"))
				failed_jira_o_entries.append(jira_entry)
			report_file.write(report_line)
		progress_bar.printProgressBar(len(jira_entries_to_log), len(jira_entries_to_log), length = 50)
		return failed_work_log_lines, failed_jira_o_entries

def refresh_jsession_id(user_name, password):
	retries = 0
	while retries < 3:
		j_session_id, login_successful = jira_helper.get_j_session_id(user_name, password)
		if (login_successful):
			return j_session_id
		retries = retries + 1
		time.sleep(2)
	print("Incorrect Username/Password")
	exit(0)

def do_retry(max_retries_done):
	if auto_retry_enabled and not max_retries_done:
		return True
	else:
		do_continue = input("Max Retries limit reached. Would you like to retry the failed work logs again? y/n ")
		return do_continue.lower() == 'y'

def log_time_with_manual_retry(jira_entries, user_name, password, j_session_id):
	remaining_estimate_cache = {}
	iteration = 0
	failed_jira_entries = jira_entries
	while True:
		failed_work_logs, failed_jira_entries = do_log_time(iteration, failed_jira_entries, j_session_id, remaining_estimate_cache)
		if (len(failed_jira_entries)>0):
			print("Following work logs were failed to be logged: ")
			for failed_work_log in failed_work_logs:
				print(failed_work_log.replace("\n", ""))
			do_continue = input("Would you like to retry the failed work logs? y/n ")
			if do_continue.lower() != 'y':
				break
			print("Retrying ........")
			j_session_id = refresh_jsession_id(user_name, password)
		else:
			break
		iteration+=1


def log_time_with_automatic_retry(jira_entries, user_name, password, j_session_id):
	remaining_estimate_cache = {}
	failed_jira_entries = jira_entries
	while len(failed_jira_entries)>0:
		for iteration in range(1, max_retries+1):
			print("Run: "+str(iteration)+", with session_id = "+str(j_session_id))
			failed_work_logs, failed_jira_entries = do_log_time(iteration, failed_jira_entries, j_session_id, remaining_estimate_cache)
			if (len(failed_jira_entries)>0):
				print("Following work logs were failed to be logged: ")
				for failed_work_log in failed_work_logs:
					print(failed_work_log.replace("\n", ""))
				if not do_retry(False):
					break
				print("Retrying ........")
				time.sleep(retry_delay_seconds)
				j_session_id = refresh_jsession_id(user_name, password)
			else:
				break
		if len(failed_jira_entries)>0 and do_retry(True):
			continue
		break
	print("the cache after: "+str(remaining_estimate_cache))


if len(sys.argv)<2:
	print("Please provide the path to input file for reading time logging data")
	exit(0)

retry_delay_seconds = app_config.retry_delay()
auto_retry_enabled = app_config.is_auto_retry()
max_retries = app_config.max_retries()
request_delay_seconds = app_config.time_logging_delay()
report_delimeter='\t'
input_file=sys.argv[1]

jira_entries = tl_parser.get_time_logging_data(input_file)
work_log_summary = tl_parser.summarize_time_work_log(jira_entries)

#print summary
total_seconds = 0
for work_log_day in work_log_summary.keys():
	print("Date ["+str(work_log_day)+"], Total Time to be logged: ["+str(date_time_utils.from_seconds(work_log_summary[work_log_day]))+"]")
	total_seconds=total_seconds+work_log_summary[work_log_day]

date_time_utils.print_accumulative_time(total_seconds)

do_continue = input("Continue to log time? y/n ")


if do_continue.lower() == 'y':
	print("Please provide JIRA credentials.")
	user_name = do_continue = input("Username: ")
	password = getpass.getpass()
	j_session_id = refresh_jsession_id(user_name, password)
	owner_id, resp_message = jira_helper.get_owner_id(user_name, j_session_id)
	if owner_id is None or len(owner_id.strip())<=0:
		print("failed to get owner_id for "+str(user_name)+", can not proceed!")
		print("Root Cause: "+str(resp_message))
		exit(0)

	print("Collecting required information...")
	tl_parser.fill_in_origin_task_id(jira_entries, j_session_id)
	print("Logging Time with following config:\n")
	current_config = "Auto Retry \t| Max Retries \t| Retry Delay \t| Time Log Delay\n{0}\t\t| {1} \t\t| {2} \t\t| {3}\n".format(auto_retry_enabled, max_retries, retry_delay_seconds, request_delay_seconds)
	print(BColors.BOLD+current_config+BColors.ENDC)

	if auto_retry_enabled:
		log_time_with_automatic_retry(jira_entries, user_name, password, j_session_id)
	else:
		log_time_with_manual_retry(jira_entries, user_name, password, j_session_id)
	print("Done")


# TODOs:
# incorporate the other work location options besides the current default work-from-home
# adjust the remaining time for major task instead of repeating time log lines
# add a config file for using any user specific configurations
# retry the failed work logs that fail due to any jira server internal errors, move the work logging code into a reusable method