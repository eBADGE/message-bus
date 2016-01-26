eBADGE Message Bus
========

This package contains the client side of the eBadge message bus. It consists of a Python library that manages the communication and maps the messages to/from Python objects, and a set of sample scripts that demonstrate the usage at both the Home Energy Hub (HEH) side and the Virtual Power Plant (VPP) or other controlling entity side.

The server side of the message bus consists of a RabbitMQ server (version 3.5 or higher) configured as described in the document "The eBADGE Message Bus - Final Version" (eBadge project deliverable D3.2.3, available at http://www.ebadge-fp7.eu/wp-content/uploads/2015/10/eBADGE-D3.2.3-Final.pdf). For more information, please refer to the eBadge project web site at http://www.ebadge-fp7.eu .


Requirements
--------------------------------

- Python 2.7.X
Python is a programming language that lets you work more quickly and integrate your systems more effectively.

- Virtualenv (recommended)
Virtualenv is a great piece of software. It allows to create some virtual environments that have many different versions of Python across the whole system and having different sets of libraries.
We will create new virtual environments with virtualenv (current version:1.11.6)

- pip 
A tool for installing and managing Python packages.

- pika (will be installed automatically by following the installation instructions below)
Pika Python AMQP Client Library
Pika is a pure-Python implementation of the AMQP 0-9-1 protocol that tries to stay fairly independent of the underlying network support library. Pika was developed primarily for use with RabbitMQ, but should also work with other AMQP 0-9-1 brokers.


Directory tree
--------------------------------
|-- ebadge_msg

|   |-- __init__.py

|   |-- comm.py

|   |-- common.py

|   |-- heh_level.py

|   |-- heh_level_ext.py

|   `-- market_level.py

|-- requirements.txt

|-- test-heh-async.py

|-- test-heh-blocking.py

|-- test-vpp-async.py

`-- test-vpp-blocking.py

Directory ebadge_msg: python bindings for message-bus

requirements.txt: Requirements file for pip tool. The file lists the required python package names and versions.

test-heh-async.py: Example script for asynchronous RabbitMQ connection on HEH side. It uses threads for simultaneous processing consumer and publisher. It sends a load_report message as a response to each get_report message that it receives from RabbitMQ.

test-vpp-async.py: Example script for asynchronous RabbitMQ connection on VPP side. It uses threads for simultaneous processing consumer and publisher. It sends a get_report message every 5 seconds and prints out all load_report messages it receives.

Installation
-------------------------------
Create and virtual environment in folder env (recommended, otherwise requirements will be installed into your main Python environment)

$ virtualenv env

$ source env/bin/activate

Install required packages with requirements file for pip

$ pip install -r requirements.txt


Usage
--------------------------------
All test-*.py scripts are used in the same manner:

$ python test-heh-async.py <RabbitmqIP> <HehName> <Path to cert file> <Path to key file>

Example:

$ python test-heh-async.py 172.21.0.35 heh-test1

To see any real message exchange, start one heh and one vpp script at the same time.

