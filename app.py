#!flask/bin/python

from flask import Flask, jsonify, json
from enum import Enum
import requests, time

app = Flask(__name__)

class State(Enum):
	home = 1
	away = 2

appState = State.home

@app.route('/orchestrate/api/v1.0/getState', methods=['GET'])
def getState():
    return '\n Current state is: ' + appState.name + '\n\n'

@app.route('/orchestrate/api/v1.0/push', methods=['POST'])
def run():
    global appState
    if appState == State.home:
        goAway()
        appState = State.away
        print appState.name
        return '\n on the way to the horizon'
    elif appState == State.away:
        goHome()
        appState = State.home
        return '\n on the way home'

@app.route('/orchestrate/api/v1.0/dock', methods=['POST'])
def docking():
    # kill running nodes
    # start docking nodes 
    #invoceCommandOnRobot('/home/turtlebot/launch_nodekill.sh')
    #time.sleep(5)
    invoceCommandOnRobot('/home/turtlebot/launch_docking.sh')
    return 'docking now'

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def getToken():
    tokenUrl = 'http://ab44513583e1711e6b0ef02e4cf15b02-1319127330.eu-central-1.elb.amazonaws.com:8001/login'

    headers = {'Accept': 'application/json'}

    payload  = {'username':'roboreg',
        'password':'splab',
        'eauth':'pam'
                }
    r = requests.post(tokenUrl, headers=headers, data=payload)

    return r.headers['X-Auth-Token']

def goAway():
    invoceCommandOnRobot('/home/turtlebot/launch_minimal.sh')
    time.sleep(5)
    invoceCommandOnRobot('/home/turtlebot/launch_amcl.sh')
    time.sleep(5)
    invoceCommandOnRobot('/home/turtlebot/launch_moveto_away.sh')
    # publish to a move_base topic

def goHome():
    invoceCommandOnRobot('/home/turtlebot/launch_moveto_home.sh')
    

def invoceCommandOnRobot(command):
    url = 'http://ab44513583e1711e6b0ef02e4cf15b02-1319127330.eu-central-1.elb.amazonaws.com:8001'

    headers = {'Accept': 'application/json',
               'X-Auth-Token': '' + getToken() + ''
               }

    payload = {'client':'local',
               'tgt':'*',
               'fun':'cmd.run_bg',
               'arg':[command]
               }

    r = requests.post(url, headers=headers, data=payload)

    print 'started node'

if __name__ == '__main__':
    app.run(debug=True)
