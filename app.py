#!flask/bin/python

from flask import Flask, jsonify, json, request
from flask_cors import CORS
from enum import Enum
import requests, time

app = Flask(__name__)

cors = CORS(app, resources={r"/orchestrate/api/v1.0/*": {"origins": "*"}})

class State(Enum):
	home = 1
	away = 2

appState = State.home


'''
get the current application state 
return State
'''
@app.route('/orchestrate/api/v1.0/getState', methods=['GET'])
def getState():
    return '\n Current state is: ' + appState.name + '\n\n'


'''
used to push the robot to a certain position and when pushed again, 
return to the starting position
'''
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


'''
if the robot fails and gets lost the application state can be set manually. 
used only for debugging the application
'''
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

'''
if the robot is close to his docking station he can be docked
'''
@app.route('/orchestrate/api/v1.0/dock', methods=['POST'])
def docking():
    invoceCommandOnRobot('/home/turtlebot/launch_docking.sh')
    return 'docking now'

'''
startup the minimal + the amcl nodes on the robot
'''
@app.route('/orchestrate/api/v1.0/startUp', methods=['POST'])
def startUp():
    invoceCommandOnRobot('/home/turtlebot/launch_minimal_amcl.sh')
    return 'starting up...'

'''
startup the required nodes on the kubernetes cluster
'''
@app.route('/orchestrate/api/v1.0/createKubeNodes', methods=['POST'])
def createKubeNodes():
    # create ROS Master
    createKubeNode('/demoApp/kubernetes/ros_master/master_svc.json')
    createKubeNode('/demoApp/kubernetes/ros_master/master_pod.json')
    

'''
returns the robot back to his starting point. 
'''
@app.route('/orchestrate/api/v1.0/goBack', methods=['POST'])
def goBack():
    invoceCommandOnRobot('/home/turtlebot/launch_moveto_home.sh')
    return 'on the way home'


'''
standart 404 error handler
'''
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def createKubeNode(nodeDescription):
    url = 'https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/default/pods'

    headers = {'Authorization': 'Bearer $KUBE_TOKEN',
               'Content-Type': 'application/json'
               }

    r = requests.post(url, data=open(nodeDescription, 'rb'), headers=headers)


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
