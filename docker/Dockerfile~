FROM ubuntu:14.04.4

# Update the sources list
RUN apt-get update

# Install basic applications
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python2.7 python-pip

# clone the webapp
RUN git clone https://github.com/loeh/e2eTurtlebotWebApp.git /webapp

# Get pip to download and install requirements:
RUN pip install -r /webapp/requirements.txt

# Copy kubernetes config
COPY config /root/.kube/

# Copy kubectl bin
COPY kubectl /usr/local/bin

# Install Helm
RUN export HELM_OS=linux && wget https://github.com/kubernetes/helm/releases/download/v2.0.0-alpha.4/helm-v2.0.0-alpha.4-$HELM_OS-amd64.tar.gz && tar -zxvf helm-v2.0.0-alpha.4-$HELM_OS-amd64.tar.gz && cd $HELM_OS-amd64

# Init Helm
RUN cd /linux-amd64 && ./helm init --client-only

# Copy Turtlebot chart
COPY e2eTurtlebot /root/

# Expose ports
EXPOSE 5000 8080

# Set the default directory where CMD will execute
WORKDIR /webapp

CMD python server.py
