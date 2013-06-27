#!/bin/bash
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cd /

CLOUD_STORAGE=%s
JMETER_DIR=apache-jmeter-2.8-server

# Set up Open JDK
mkdir -p jre
JRE_HEADLESS=openjdk-6-jre-headless_*.deb
JRE_LIB=openjdk-6-jre-lib_*.deb
gsutil -m cp $CLOUD_STORAGE/$JRE_HEADLESS $CLOUD_STORAGE/$JRE_LIB jre
dpkg -i --force-depends jre/*.deb

# Download JMeter server package
gsutil cp $CLOUD_STORAGE/$JMETER_DIR.tar.gz .
tar zxf $JMETER_DIR.tar.gz
cd $JMETER_DIR

# Get this server's ID from Compute Engine metadata.
ID=$(curl http://metadata/computeMetadata/v1beta1/instance/attributes/id)

perl -pi -e "s/{{SERVER_PORT}}/24000+$ID/e" bin/jmeter.properties
perl -pi -e "s/{{SERVER_RMI_PORT}}/26000+$ID/e" bin/jmeter.properties

# Start JMeter server.
bin/jmeter-server -Djava.rmi.server.hostname=127.0.0.1
