import requests
import date_time_utils

JIRA_BASE_URL="https://jira.gk-software.com/"

def get_owner_id(user_name, j_session_id):
    try:
        url = JIRA_BASE_URL+"/rest/api/2/user"

        querystring = {"username":user_name}

        headers = {
            'cookie': "JSESSIONID="+j_session_id+""
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        if (response.status_code==401):
            return None, "Authentication Failed"
        return response.json()['key'], "success"
    except Exception as e:
        return None, str(e)

def get_j_session_id(user_name, password):
    try:
        login_url = JIRA_BASE_URL+"login.jsp"

        payload = {
            "os_username": user_name, 
            "os_password": password, 
            "login": "Log In"
        }
        
        response = requests.request("POST", login_url, data=payload)
        if (response.headers['X-Seraph-LoginReason'] == 'AUTHENTICATED_FAILED'):
            return None, False
        return response.headers['Set-Cookie'].split(";")[0].split("=")[1].strip(), True
    except Exception as e:
        return None, False

def get_origin_task_id(jira_id, j_session_id):
    url = JIRA_BASE_URL+"rest/api/2/issue/"+jira_id
    headers = {
    'cookie': "JSESSIONID="+j_session_id
    }
    response = requests.request("GET", url, headers=headers)
    if response is not None and response.ok:
        origin_task_id=response.json()['id']
        return (origin_task_id, "success. origin_task_id = "+str(origin_task_id))
    else:
        return (0, "Unauthorized (401)" if response.status_code==401 else str(response.text))

def log_time(jira_entry, remaining_estimate, j_session_id, owner_id):

    payload = "{\"attributes\":{\"_WorkLocation_\":"+\
    "{\"name\":\"Work Location\","+\
    "\"workAttributeId\":1,"+\
    "\"value\":\"Home_Office\"}},"+\
    "\"billableSeconds\":\"\","+\
    "\"worker\":\""+owner_id+"\","+\
    "\"comment\":\""+jira_entry.description+"\","+\
    "\"started\":\""+date_time_utils.get_start_date_time(jira_entry.issue_date, jira_entry.start_time)+"\","+\
    "\"timeSpentSeconds\":"+str(date_time_utils.get_time_elapsed_in_seconds(jira_entry.start_time, jira_entry.end_time))+","+\
    "\"originTaskId\":\""+str(jira_entry.origin_task_id)+"\","+\
    "\"remainingEstimate\":"+str(remaining_estimate)+","+\
    "\"endDate\":null,"+\
    "\"includeNonWorkingDays\":false}"

    url = JIRA_BASE_URL+"rest/tempo-timesheets/4/worklogs/"

    headers = {
        'accept': "application/json, application/vnd-ms-excel",
        'content-type': "application/json",
        'cookie': "_ga=GA1.2.226658058.1639642505; _gid=GA1.2.685119408.1644171038; lmdatacda723fd03e01dd53d155f3d4387efb2=87e76babaf22ec586fbcdd470b9f03db;"+\
                  " JSESSIONID="+j_session_id+"; atlassian.xsrf.token=BFNZ-8P80-TI0H-K11S_9cabe7beb47166333e3f2d12d3f162fd1617df7b_lin"
        }
    try:
        response = requests.request("POST", url, data=payload, headers=headers)
        if (response):
            return ("Successful", "time log successful", response.status_code)

        if (response is not None):
            return ("Failed", "time log unsuccessful. http_status: "+str(response.status_code)+", response: "+str(response)+", reason: "+str(response.reason), response.status_code)
    except Exception as e:
        return ("Failed", "time log unsuccessful. ", 500)

#will either return the current remaining eastimation time
#or return None in case the remaining estimation couldn't be extracted
#or return -1 if the remaining estimation is not defined for a Jira issue
def get_remaining_estimate(jira_entry, j_session_id):
    payload = "{"\
    +"\"jql\":\"issue in ("+str(jira_entry.origin_task_id)+")\","+\
    "\"fields\":[\"timeestimate\",\"timeoriginalestimate\",\"timetracking\"],"+\
    "\"startAt\":0,"+\
    "\"maxResults\":1}"
    headers = {
        'accept': "application/json, application/vnd-ms-excel",
        'content-type': "application/json",
        'cookie': "_ga=GA1.2.226658058.1639642505; _gid=GA1.2.685119408.1644171038; lmdatacda723fd03e01dd53d155f3d4387efb2=87e76babaf22ec586fbcdd470b9f03db;"+\
                  " JSESSIONID="+j_session_id+"; atlassian.xsrf.token=BFNZ-8P80-TI0H-K11S_9cabe7beb47166333e3f2d12d3f162fd1617df7b_lin"
        }
    url = JIRA_BASE_URL+"rest/api/2/search/"
    try:
        response = ""
        response = requests.request("POST", url, data=payload, headers=headers)
        remaining_estimate = _extract_remaining_estimate(response)
        if remaining_estimate is None:
            return ("Failed", "Failed to get remaining estimate for "+str(jira_entry.issue_id), remaining_estimate, response.status_code)
        if remaining_estimate == -1:
            return ("Successful", "Remaining estimate isn't defined for issue: "+str(jira_entry.issue_id), remaining_estimate, response.status_code)
        time_spent_seconds = date_time_utils.get_time_elapsed_in_seconds(jira_entry.start_time, jira_entry.end_time)
        if (remaining_estimate < time_spent_seconds):
            # warn about the remaining estimate being over?
            remaining_estimate = 0
        else:
            remaining_estimate = remaining_estimate - time_spent_seconds
        return ("Successful", "success. remaining_estimate = "+str(remaining_estimate), remaining_estimate, response.status_code)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        response_code = "unknown"
        if response is not None and type(response) is not str:
            response_code = response.status_code
        return ("Failed", "Failed to get remaining estimate for "+str(jira_entry.issue_id), 0, response_code)


#returning -1 means remaining estimate isn't defined for this issue
def _extract_remaining_estimate(response):
    if response.json() is not None:
        if "issues" in response.json() and len(response.json()['issues'])>0:
            issue_details = response.json()['issues'][0]
            if "fields" in issue_details and "timeestimate" in issue_details['fields']:
                if issue_details['fields']['timeestimate'] is None:
                    return -1
                else:
                    return issue_details['fields']['timeestimate']
    return None
