import datetime


def validate_time_range(start_time, end_time): 
	try:
		if datetime.datetime.strptime(start_time, '%H:%M').time() < datetime.datetime.strptime(end_time, '%H:%M').time():
			return (True, "time range is valid");
		else:
			return (False, "Issue end time is earlier than start time")
		return  
	except Exception as e:
		return (False, str(e))

	

def get_date_obj(date): 
	return datetime.datetime.strptime(date, '%d/%m/%y').date() 

def get_time_obj(time):
	return datetime.datetime.strptime(time, '%H:%M').time()

def get_time_elapsed_in_seconds(start_time, end_time):
	date = datetime.date(1, 1, 1)
	datetime_start = datetime.datetime.combine(date, start_time)
	datetime_end = datetime.datetime.combine(date, end_time)
	time_elapsed = datetime_end - datetime_start
	return time_elapsed.seconds

def from_seconds(seconds):
	return datetime.timedelta(seconds=seconds)

def get_start_date_time(start_date, start_time):
	return str(start_date)+"T"+str(start_time)+".000"


def print_accumulative_time(total_seconds):
	total_accumulative_time = from_seconds(total_seconds)
	hours = str(from_seconds(total_accumulative_time.seconds))
	print("Accumulated Time: "+str((total_accumulative_time.days*24) + int(hours.split(":")[0]))+":"+str(hours.split(":")[1]))
