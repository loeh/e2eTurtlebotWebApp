#!flask/bin/python

from flask import Flask, jsonify, json, request
import requests, time, os, yaml, subprocess, logging

authToken = None

'''
setter for a new auth token used in salt
'''
def setCurrentToken(token):
    global authToken
    authToken = token

'''
convert yaml files to json
@param yaml file
return jsonString
'''
def convertYmlToJson(ymlFile):
   with open(ymlFile, 'r') as stream:
        try:
            jsonString = json.dumps(yaml.load(stream), indent=2)
            print(jsonString)
            return jsonString
        except yaml.YAMLError as exc:
            print(exc)

'''
create a now pod or service in the current kubernetes cluster
@param json description of the node/service
'''
def createKubeNode(nodeDescription):

    KUBERNETES_SERVICE_HOST = os.environ.get('KUBERNETES_SERVICE_HOST')
    KUBERNETES_PORT_443_TCP_PORT = os.environ.get('KUBERNETES_PORT_443_TCP_PORT')
    f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')
    KUBE_TOKEN = f.read()

    url = 'https://' + KUBERNETES_SERVICE_HOST + ':' + KUBERNETES_PORT_443_TCP_PORT + '/api/v1/namespaces/default/pods'

    headers = {'Authorization': 'Bearer ' + KUBE_TOKEN,
               'Content-Type': 'application/json'
               }

    #r = requests.post(url, data=open(nodeDescription, 'rb'), headers=headers, verify=False)
    r = requests.post(url, data=nodeDescription, headers=headers, verify=False)

'''
install e2eTurtlebot chart using helm
'''
def installNodes():
    subprocess.call(["helm", "install", "/root/e2eTurtlebot"])

'''
remove e2eTurtlebot chart using helm
'''
def removeNodes():
    releaseName = subprocess.check_output(["helm", "list"])
    releaseNameString = str(releaseName)
    releaseNameString = releaseNameString.rstrip()
    subprocess.call(["helm", "delete", releaseNameString])

'''
get the domain name of an loadBalancer ingress
@param serviceName
return String domain name
'''
def getServiceEndPoint(serviceName):

    KUBERNETES_SERVICE_HOST = os.environ.get('KUBERNETES_SERVICE_HOST')
    KUBERNETES_PORT_443_TCP_PORT = os.environ.get('KUBERNETES_PORT_443_TCP_PORT')
    f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')
    KUBE_TOKEN = f.read()

    url = 'https://' + KUBERNETES_SERVICE_HOST + ':' + KUBERNETES_PORT_443_TCP_PORT + '/api/v1/namespaces/default/services/'+serviceName

    headers = {'Authorization': 'Bearer ' + KUBE_TOKEN,
               'Content-Type': 'application/json'
               }

    r = requests.get(url, headers=headers, verify=False)
    jsonData = r.json()
    return jsonData['status']['loadBalancer']['ingress'][0]['hostname']

'''
create new Salt Token to authenticate to the saltmaster
'''
def createToken():
    tokenUrl = 'http://a8ebe290c549111e69b640206bb85836-998418534.eu-central-1.elb.amazonaws.com:8001/login'

    headers = {'Accept': 'application/json'}

    payload  = {'username':'roboreg',
        'password':'splab',
        'eauth':'pam'
                }
    r = requests.post(tokenUrl, headers=headers, data=payload)

    return r.headers['X-Auth-Token']

'''
invoce new command on the robot using salt.
@param command to execute on the robot
'''
def invoceCommandOnRobot(command):

    url = 'http://a8ebe290c549111e69b640206bb85836-998418534.eu-central-1.elb.amazonaws.com:8001'

    headers = {'Accept': 'application/json',
               'X-Auth-Token': '' + authToken + ''
               }

    payload = {'client':'local',
               'tgt':'*',
               'fun':'cmd.run_bg',
               'arg':[command]
               }

    r = requests.post(url, headers=headers, data=payload)

    print 'started node'
