#!flask/bin/python

from flask import Flask, jsonify, json, request
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
        return '\n on the way to the horizon \n\n'
    elif appState == State.away:
        goHome()
        appState = State.home
        return '\n on the way home \n\n'

@app.route('/orchestrate/api/v1.0/setState', methods=['POST'])
def setState():
    global appState
    if request.args.get('state') == 'home':
        appState = State.home
        return '\n state is set to home \n\n'
    elif request.args.get('state') == 'away':
        appState = State.away
        return '\n state is set to away \n\n'
    else:
        return '\n wrong parameter \n\n'

@app.route('/orchestrate/api/v1.0/dock', methods=['POST'])
def docking():
    invoceCommandOnRobot('/home/turtlebot/launch_docking.sh')
    return 'docking now'

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def getToken():
    tokenUrl = 'http://a8ebe290c549111e69b640206bb85836-998418534.eu-central-1.elb.amazonaws.com:8001/login'

    headers = {'Accept': 'application/json'}

    payload  = {'username':'roboreg',
        'password':'splab',
        'eauth':'pam'
                }
    r = requests.post(tokenUrl, headers=headers, data=payload)

    return r.headers['X-Auth-Token']

def goAway():
    invoceCommandOnRobot('/home/turtlebot/launch_minimal_amcl.sh')
    time.sleep(5)
    invoceCommandOnRobot('/home/turtlebot/launch_moveto_away.sh')
    # publish to a move_base topic

def goHome():
    invoceCommandOnRobot('/home/turtlebot/launch_moveto_home.sh')
    

def invoceCommandOnRobot(command):
    url = 'http://a8ebe290c549111e69b640206bb85836-998418534.eu-central-1.elb.amazonaws.com:8001'

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
