# Dropbox
This is a simple, secure, and multithreaded system designed to upload and manage files on a remote server. The system consists of both a server and a client, communicating via a custom protocol to transfer files efficiently.

## Features
- **Multithreaded:** Support for handling multiple users concurrently.
- **Custom Protocol:** Dedicated protocol for secure file transfers.
- **Simple & Secure:** Easy-to-use interface with secure data transmission.

## Before starting
First of all, install dropbox package. The required dependencies will be installed automatically. Run the following commands in your terminal:
```shell
cd dropbox
sudo python3 -m pip install -e .
```

## Server Usage
To run the server, use the following command:
```shell
sudo python3 server.py [-h] [--address IP_ADDRESS] [--port PORT]
```
### Optional arguments
* `-p` or `--port`: Specify the port that the server will listen on. The default port is 8000. 
* `-i` or `--ip-address`: Define the IP address the server will bind to. The default is 127.0.0.1.


## Client Usage
To connect a client to the server, run:
```shell
sudo python3 client.py [-h] [--address IP_ADDRESS] [--port PORT]
```
### Optional arguments
* `-p` or `--port`: Specify the server port to connect to. Default is 8000.
* `-i` or `--ip-address`: Define the server IP address to connect to. Default is 127.0.0.1.

## Testing environment
This project includes both system and unit tests, which validate the software under various scenarios and edge cases.

### System tests
To run system tests, execute the following commands:
```shell
cd dropbox/dropbox_testing/system_tests/tests
pytest <file_name>
```

### Unit tests
To run unit tests, execute the following commands:
```shell
cd dropbox/dropbox_testing/unit_tests
python3 <file_name>
```
