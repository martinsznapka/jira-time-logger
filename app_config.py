from jproperties import Properties
from bcolors import BColors


app_config = Properties()

with open("appconfig.properties", "r+b") as config_file:
	try:
		app_config.load(config_file, "utf-8")
	except Exception as ex:
		print(BColors.FAIL+"Error: Couldn't load application config"+BColors.ENDC)
		print("An exception of type {0} occurred. Arguments:\n{1!r}".format(type(ex).__name__, ex.args))
		exit(0)

def time_logging_delay():
	key = "time.logging.delay"
	try:
		if key in app_config:
			if app_config[key][0].strip().isdigit():
				return int(app_config[key][0].strip())
			else:
				raise ValueError('{0} is not a valid Integer for config {1}'.format(app_config[key][0], key))
		else:
			raise ValueError('No config for {0} is defined in application config'.format(key))
	except Exception as ex:
		print(BColors.FAIL+"Error: Couldn't load config for "+key+BColors.ENDC)
		print("An exception of type "+BColors.HEADER+type(ex).__name__+BColors.ENDC+" occurred. Arguments: "+BColors.HEADER+ex.args[0]+BColors.ENDC)
		exit(0)

def is_auto_retry():
	key = "retry.auto"
	try:
		if key in app_config:
			return app_config[key][0].lower().strip() == 'true'
		else:
			raise ValueError('No config for {0} is defined in application config'.format(key))
	except Exception as ex:
		print(BColors.FAIL+"Error: Couldn't load config for "+key+BColors.ENDC)
		print("An exception of type "+BColors.HEADER+type(ex).__name__+BColors.ENDC+" occurred. Arguments: "+BColors.HEADER+ex.args[0]+BColors.ENDC)
		exit(0)

def retry_delay():
	key = "retry.delay"
	try:
		if key in app_config:
			if app_config[key][0].strip().isdigit():
				return int(app_config[key][0].strip())
			else:
				raise ValueError('{0} is not a valid Integer for config {1}'.format(app_config[key][0], key))
		else:
			raise ValueError('No config for {0} is defined in application config'.format(key))
	except Exception as ex:
		print(BColors.FAIL+"Error: Couldn't load config for "+key+BColors.ENDC)
		print("An exception of type "+BColors.HEADER+type(ex).__name__+BColors.ENDC+" occurred. Arguments: "+BColors.HEADER+ex.args[0]+BColors.ENDC)
		exit(0)

def max_retries():
	key = "retry.max_attempts"
	try:
		if key in app_config:
			if app_config[key][0].strip().isdigit():
				return int(app_config[key][0].strip())
			else:
				raise ValueError('{0} is not a valid Integer for config {1}'.format(app_config[key][0], key))
		else:
			raise ValueError('No config for {0} is defined in application config'.format(key))
	except Exception as ex:
		print(BColors.FAIL+"Error: Couldn't load config for "+key+BColors.ENDC)
		print("An exception of type "+BColors.HEADER+type(ex).__name__+BColors.ENDC+" occurred. Arguments: "+BColors.HEADER+ex.args[0]+BColors.ENDC)
		exit(0)

def retry_delay_multiplier():
	key = "retry.delay.multiplier"
	try:
		if key in app_config:
			if app_config[key][0].strip().isdigit():
				return int(app_config[key][0].strip())
			else:
				raise ValueError('{0} is not a valid Integer for config {1}'.format(app_config[key][0], key))
		else:
			raise ValueError('No config for {0} is defined in application config'.format(key))
	except Exception as ex:
		print(BColors.FAIL+"Error: Couldn't load config for "+key+BColors.ENDC)
		print("An exception of type "+BColors.HEADER+type(ex).__name__+BColors.ENDC+" occurred. Arguments: "+BColors.HEADER+ex.args[0]+BColors.ENDC)
		exit(0)

def log_line_delimeter():
	key = "parser.log.line.delimeter"
	try:
		if key in app_config:
			return app_config[key][0].strip()
		else:
			raise ValueError('No config for {0} is defined in application config'.format(key))
	except Exception as ex:
		print(BColors.FAIL+"Error: Couldn't load config for "+key+BColors.ENDC)
		print("An exception of type "+BColors.HEADER+type(ex).__name__+BColors.ENDC+" occurred. Arguments: "+BColors.HEADER+ex.args[0]+BColors.ENDC)
		exit(0)
