FROM ubuntu:14.04.4

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python2.7 python-pip

# clone the webapp
RUN git clone https://github.com/loeh/e2eTurtlebotWebApp.git /webapp
RUN git clone https://github.com/loeh/e2eTurtlebotDemo.git /demoApp

# Get pip to download and install requirements:
RUN pip install -r /webapp/requirements.txt

# Expose ports
EXPOSE 5000

# Set the default directory where CMD will execute
WORKDIR /webapp

CMD python server.py
