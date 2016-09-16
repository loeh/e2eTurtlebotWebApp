#!flask/bin/python

from flask import Flask, jsonify, json, request
from flask_cors import CORS
from enum import Enum
import requests, time, os, yaml
from helper import *

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
def dock():
    invoceCommandOnRobot('/home/turtlebot/stop_minimal_amcl.sh')
    time.sleep(5)
    invoceCommandOnRobot('/home/turtlebot/launch_docking.sh')
    time.sleep(5)
    invoceCommandOnRobot('/home/turtlebot/activate_docking.sh')
    return 'docking now'

'''
if the robot is succefully docked, kill all the docking nodes
'''
@app.route('/orchestrate/api/v1.0/docked', methods=['POST'])
def docked():
    invoceCommandOnRobot('/home/turtlebot/stop_docking.sh')
    invoceCommandOnRobot('/home/turtlebot/stop_rrbridge.sh')
    return 'killed the docking nodes'

'''
startup the minimal + the amcl nodes on the robot
'''
@app.route('/orchestrate/api/v1.0/startUp', methods=['POST'])
def startUp():
    invoceCommandOnRobot('/home/turtlebot/launch_minimal_amcl.sh')
    invoceCommandOnRobot('/home/turtlebot/launch_rrbridge.sh')
    return 'starting up the robot...\n\n'

'''
startup the required nodes on the kubernetes cluster
'''
@app.route('/orchestrate/api/v1.0/createKubeNodes', methods=['POST'])
def createKubeNodes():
    # create ROS Master
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/ros_master/master_svc.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/ros_master/master_pod.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/rrbridge/bridge_svc.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/rrbridge/bridge_pod.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/ros_posePublisher/ros_posePublisher_svc.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/ros_posePublisher/ros_posePublisher_pod.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/ros_bridge/ros_bridge_svc_headless.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/ros_bridge/ros_bridge_svc_public.yml'))
    createKubeNode(convertYmlToJson('/demoApp/kubernetes/ros_bridge/ros_bridge_pod.yml'))
    return 'started required nodes\n\n'


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


def goAway():
    invoceCommandOnRobot('/home/turtlebot/launch_minimal_amcl.sh')
    time.sleep(5)
    invoceCommandOnRobot('/home/turtlebot/launch_moveto_away.sh')
    # publish to a move_base topic

def goHome():
    invoceCommandOnRobot('/home/turtlebot/launch_moveto_home.sh')


if __name__ == '__main__':
    app.run(debug=True)
