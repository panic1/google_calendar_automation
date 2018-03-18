#!/usr/bin/env python2

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

from ConfigParser import RawConfigParser, NoSectionError, NoOptionError
import dateutil.parser
import pytz
import subprocess

from enum import Enum

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar Automation'
CALENDAR_CONF_FILE = 'calendar.conf'

class State(Enum):
    INACTIVE = 0
    STARTING = 1
    STOPPING = 2
    ACTIVE   = 3

def get_config():
    conf = RawConfigParser()
    conf.read(CALENDAR_CONF_FILE)

    return conf

def get_calendarId(conf, section):
    """Gets the calendarId from the configuration

    if nothing is found, the default will be "primary"
    """
    
    try:
        return conf.get(section, "calendarId")
    except:
        print("Could not find the calendarId in the configuration file, default to primary")
        return "primary"

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_events(calendarId, max_results):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    eventsResult = service.events().list(
        calendarId=calendarId, timeMin=now, maxResults=max_results, singleEvents=True,
        orderBy='startTime').execute()
    return eventsResult.get('items', [])

def get_state(conf, section):
    cmd = conf.get(section, 'status')
    print("checking things: {}".format(cmd))
    returnstr = subprocess.check_output(conf.get(section, 'status'), shell=True)
    print("checking things: {}".format(returnstr))
    
    return State(int(returnstr))

def run_start(conf, section):
    cmd = conf.get(section, 'start')
    print("starting things: {}".format(cmd))
    subprocess.call(cmd, shell=True)

def run_end(conf, section):
    cmd = conf.get(section, 'end')
    print("stopping things: {}".format(cmd))
    subprocess.call(cmd, shell=True)

def main():
    conf = get_config()

    # for section in conf.sections():
    section = conf.sections()[0]  # for now only run for the first section in the configuration
    events = get_events(get_calendarId(conf, section), 10)
    
    now = datetime.datetime.now(pytz.utc)
    delta = datetime.timedelta(minutes=2)
    in_progress = False
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = dateutil.parser.parse(event['start']['dateTime']) - delta
        end = dateutil.parser.parse(event['end']['dateTime']) + delta
        if (now >= start and now < end):
            in_progress = True

    state = get_state(conf, section)

    if (in_progress):
        # a calendar item is in progress right now, if the state is not active then start it
        if (state == State.INACTIVE or state == State.STOPPING):
            run_start(conf, section)
    else:
        # a calendar item is not in progress now, if the state is active then end it
        if (state == State.ACTIVE or state == State.STARTING):
            run_end(conf, section)

if __name__ == '__main__':
    main()

