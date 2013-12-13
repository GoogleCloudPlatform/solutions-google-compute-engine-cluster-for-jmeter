Google Compute Engine Cluster for JMeter
========================================


Copyright
---------

Copyright 2013 Google Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Disclaimer
----------

This sample application is not an official Google product.


Summary
-------

Apache JMeter is an open source framework for load testing.  It's designed to
apply load from distributed JMeter servers simultaneously.

The application sets up a Google Compute Engine cluster and starts the JMeter
servers on them.  It can also start JMeter client on the local machine
where the application is executed.  JMeter client controls JMeter servers,
starting and stopping the load, and collecting statistical information
from JMeter servers.

The system (JMeter server cluster and JMeter client) works as a load testing
framework over the target system.  JMeter supports various protocols, including
HTTP, FTP, SMTP and JDBC.  The test target can be any system that can be
accessed from Google Compute Engine instances via network, such as servers
installed on Google Compute Engine, a Google App Engine application, or
publicly accessible servers outside Google Cloud Platform.

In order for the JMeter client to communicate with JMeter servers on Google
Compute Engine instances, SSH tunnels must be set up properly.  The application
automatically sets up SSH tunnels.  It also automatically configures JMeter
client, so that it can properly control JMeter servers.


Prerequisites
-------------

The application assumes Google Cloud Storage and Google Compute Engine services
are enabled.

To create a new project, go to the
[Google Cloud Console](https://cloud.google.com/console) and click red
"CREATE PROJECT" button at top left.  When a new project is created, click
"Compute Engine" and turn on billing to enable Google Compute Engine
on the new project.

The application requires sufficient Google Compute Engine instance and CPU quota
to set up JMeter server cluster on Google Compute Engine.
Note that the default instances used by the application have 2 CPUs each.

The application requires [gcutil](https://developers.google.com/compute/docs/gcutil/)
command line tool.  In addition, setting up
[gsutil](https://developers.google.com/storage/docs/gsutil)
is also helpful to set up the application, although gsutil is not a requirement.

##### `gcutil` configuration

If this is the first time running `gcutil` for the project, run the following
command to authorize `gcutil` to access the project.

    gcutil auth --project=<project ID>

Default project of gcutil must be set to the project where JMeter servers
are started.  The following command
[sets gcutil default project](https://developers.google.com/compute/docs/gcutil/#project).

    gcutil getproject --project=<project ID> --cache_flag_values

If this is the first time using `gcutil` for operation that requires SSH
credentials (such as "gcutil addinstance" or "gcutil ssh"), gcutil creates
new SSH credentials.  At that time, passphrase is asked.
The **passphrase must be empty** for the application to work properly.
If SSH credentials with passphrase already exists for gcutil, the application
fails to establish SSH forwarding.  In this case, remove existing credentials
at `~/.ssh/google_compute_engine*` and re-create SSH credentials.


Set-Up Instruction
------------------

### Download and set up Python libraries

The following libraries are required by the application, and here is an
example of how to set up libraries in the application directory.  The commands
below need to be executed from the top directory of the application.

##### Google Client API

[Google Client API](http://code.google.com/p/google-api-python-client/)
is library to access various Google's services via API.

Download google-api-python-client-1.2.tar.gz from
[download page](http://code.google.com/p/google-api-python-client/downloads/list)
or by the following command.

    curl -O http://google-api-python-client.googlecode.com/files/google-api-python-client-1.2.tar.gz

Set up the library in `compute_engine_cluster_for_jmeter` directory.

    tar zxf google-api-python-client-1.2.tar.gz
    ln -s google-api-python-client-1.2/apiclient .
    ln -s google-api-python-client-1.2/oauth2client .
    ln -s google-api-python-client-1.2/uritemplate .

##### Httplib2

[Httplib2](https://code.google.com/p/httplib2/) is used by Google Client API
internally.
Download httplib2-0.8.tar.gz from
[download page](https://code.google.com/p/httplib2/downloads/list).
or by the following command.

    curl -O https://httplib2.googlecode.com/files/httplib2-0.8.tar.gz

Set up the library in `compute_engine_cluster_for_jmeter` directory.

    tar zxf httplib2-0.8.tar.gz
    ln -s httplib2-0.8/python2/httplib2 .

##### Python gflags

[gflags](http://code.google.com/p/python-gflags/) is used by Google Client API
internally.
Download python-gflags-2.0.tar.gz from
[download page](http://code.google.com/p/python-gflags/downloads/list).
or by the following command.

    curl -O http://python-gflags.googlecode.com/files/python-gflags-2.0.tar.gz

Set up the library in `compute_engine_cluster_for_jmeter` directory.

    tar zxf python-gflags-2.0.tar.gz
    ln -s python-gflags-2.0/gflags.py .
    ln -s python-gflags-2.0/gflags_validators.py .

##### Python mock (required only for unit tests)

[mock](https://pypi.python.org/pypi/mock) is mocking library for Python.
It will be included in Python as standard package from Python 3.3.
However, since the application uses Python 2.7, it needs to be set up.

Download mock-1.0.1.tar.gz from
[download page](https://pypi.python.org/pypi/mock#downloads).
or by the following command.

    curl -O https://pypi.python.org/packages/source/m/mock/mock-1.0.1.tar.gz

Set up the library in `compute_engine_cluster_for_jmeter` directory.

    tar zxf mock-1.0.1.tar.gz
    ln -s mock-1.0.1/mock.py .

### Prepare Google Cloud Storage bucket

Create a Google Cloud Storage bucket, from which Google Compute Engine instance
downloads required packages for set up JMeter server.

This can be done one of the following ways:

* Using existing bucket.
* Creating new bucket from Google Cloud Storage Web UI.  Go to
[Google Cloud Console](https://cloud.google.com/console), choose a project,
and go to "Cloud Storage" page.  A new bucket can be created by clicking
the red "NEW BUCKET" button at top left.
* Creating new bucket by
[gsutil command line tool](https://developers.google.com/storage/docs/gsutil).
`gsutil mb gs://<bucket name>`

Make sure to create the bucket in the same project as Google Compute Engine
instances are started.

### Prepare JMeter packages

Download
[JMeter 2.9](http://archive.apache.org/dist/jmeter/binaries/apache-jmeter-2.9.tgz)
from the link or by command line.

    curl -O http://archive.apache.org/dist/jmeter/binaries/apache-jmeter-2.9.tgz

In the application, 2 sets of JMeter packages are required, one for server and
the other for client.  Server and client use different configurations, and
so a patch for each configuration file is provided in the downloaded package.

First, prepare client JMeter package.

    tar zxf apache-jmeter-2.9.tgz
    patch -p0 < jmeter.properties.client.patch
    mv apache-jmeter-2.9 apache-jmeter-2.9-client

Then, prepare the server package.  Archive JMeter server package to upload to
Google Cloud Storage.

    tar zxf apache-jmeter-2.9.tgz
    patch -p0 < jmeter.properties.server.patch
    mv apache-jmeter-2.9 apache-jmeter-2.9-server
    tar zcf apache-jmeter-2.9-server.tar.gz apache-jmeter-2.9-server/

The server package must be uploaded to Google Cloud Storage, so that
the Google Compute Engine instance can download and install in start-up script.
This can be done by drag-and-drop to Google Cloud Storage Web UI, or by the
following command.

    gsutil cp apache-jmeter-2.9-server.tar.gz gs://<bucket name>/

### Download Open JDK Package

The application uses [Open JDK](http://openjdk.java.net/) as Java runtime
environment.  Open JDK Java Runtime Environment is distributed under
[GNU Public License version 2](http://www.gnu.org/licenses/gpl-2.0.html).
User must agree to the license to use Open JDK.  Note that OpenJDK has different
licensing terms from the application, and user should make sure to read
and understand those terms.

Download amd64 package of openjdk-6-jre-headless, and architecture-common
package of openjdk-6-jre-lib from the following sites.

[http://packages.debian.org/wheezy/openjdk-6-jre-headless](http://packages.debian.org/wheezy/openjdk-6-jre-headless)
[http://packages.debian.org/wheezy/openjdk-6-jre-lib](http://packages.debian.org/wheezy/openjdk-6-jre-lib)

Upload .deb packages to the same Google Cloud Storage bucket.

    gsutil -m cp *.deb gs://<bucket name>/

### Create client ID and client secret

Client ID and client secret are required by OAuth2 authorization to identify
the application.  It is required in order for the application to access a
Google API (in this example, Google Compute Engine API) on behalf of the user.

Client ID and client secret can be set up from "Registered apps" under
"APIs & auth" menu in the left pane of the project page of
[Google Cloud Console](https://cloud.google.com/console).
Click the red "REGISTER APP" button at the top to create client ID and
client secret.

Type a name to distinguish the application, choose "Native" as platform
type, and click the blue "Register" button.  Client ID and client secret are
created and shown on the page.

### Change Configuration on the Application Code

`jmeter_cluster.py` includes configurations as global variables.  Some of them
must be changed to meet the environment.

* `CLIENT_ID` and `CLIENT_SECRET`
    * Set to client ID and client secret created in the previous section.
* `CLOUD_STORAGE`
    * Set to Google Cloud Storage bucket name configured for the application.
* `DEFAULT_PROJECT`
    * Project ID is found on the top left corner of
      [Google Cloud Console](https://cloud.google.com/console).


Usage of the Application
--------------------------------

#### `jmeter_cluster.py`

`jmeter_cluster.py` is the main script of the application.
It starts up Google Compute Engine instance cluster with JMeter servers,
starts JMeter client and deletes the cluster when it's no longer needed.

##### Show usage

    ./jmeter_cluster.py --help

`jmeter_cluster.py` has 4 subcommands, `start`, `client` and `shutdown`.
Please refer to the following usages for available options.

    ./jmeter_cluster.py start --help
    ./jmeter_cluster.py client --help
    ./jmeter_cluster.py shutdown --help

##### Start cluster

'start' subcommand starts JMeter server cluster.  By default, it starts
a cluster with 3 Google Compute Engine instances.

    ./jmeter_cluster.py start [number of workers] [--prefix <prefix>]

If the instance is started for the first time, the script requires log in
and asks for authorization to access Google Compute Engine.
By default, it opens Web browser for this procedure.
If the script is run in remote host on terminal (on SSH, for example),
it cannot open Web browser on local machine.
In this case, `--noauth_local_webserver` option can be specified as instructed
by the message as follows.

    ./jmeter_cluster.py --noauth_local_webserver start [number of workers] [--prefix <prefix>]

It avoids the attempt to open local Web browser, and it shows URL for
authentication and authorization.
When authorization is successful on the Web browser, the page shows
code to paste on the terminal.
By pasting the correct code, authorization process is complete in the script.
The script can then access Google Compute Engine through API.

##### Start JMeter client

'client' subcommand starts JMeter client on the local computer where
`jmeter_cluster.py` is executed.

    ./jmeter_cluster.py client

The command opens JMeter client window, which allows to control JMeter
servers on Google Compute Engine instances.

The following is an example to run load test against HTTP Web server.
The Web server to test should be prepared by the user.  Google App Engine
Web application is a great candidate to test.

1. In the left pane, right click on "Test Plan", "Add" -> "Threads (Users)"
-> "Thread Group"
2. Right-click on "Thread Group", "Add" -> "Sampler" -> "HTTP Request"
3. Set "Server Name or IP" to the hostname of the Web server to apply load onto,
and set "Path" to "/"
4. Right-click on "Thread Group", "Add" -> "Listener" -> "Aggregate Report"
5. Change Thread Group parameters to adjust load level
6. Click "Remote Start All" button at the top (icon with 2 green triangles)
to start sending load from all JMeter servers
7. To stop the load, click "Remote Stop All" button (icon with 2 stop signs)

The full description of JMeter usage can be found on
[Apache JMeter page](http://jmeter.apache.org/usermanual/index.html).

##### Tear down cluster

'shutdown' subcommand deletes all instances in the JMeter server cluster.

    ./jmeter_cluster.py shutdown [--prefix <prefix>]

#### Unit tests

The application has 2 Python files, `jmeter_cluster.py` and `gce_api.py`.
They have corresponding unit tests, `jmeter_cluster_test.py` and
`gce_api_test.py` respectively.

Unit tests can be directly executed.

    ./jmeter_cluster_test.py
    ./gce_api_test.py

Note some unit tests simulate error conditions, and those tests shows
error messages.
