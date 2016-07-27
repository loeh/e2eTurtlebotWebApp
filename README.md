# e2eTurtlebotWebApp

A Python web-app which is running on flask. 
It serves a API to invoce actions with the big reg button used in the e2eTurtlebotDemo.
invoce a post request on this REST-endpoint to invoce a state change for the e2eTurtlebotDemo.
```
 /orchestrate/api/v1.0/push 
```

At first the required nodes on the robot are started on the robot using salt commands. 
Then a goal is published to the move_base topic on the robot. When the goal is reached, 
the button can be pushed again the move the robot back to his starting position.


