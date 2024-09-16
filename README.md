# SSH & Web Honeypot Project

This project contains a low-interaction honeypot designed to capture unauthorized access attempts through SSH and a web login page. You can run it locally to test or deploy it on a server to gather real-world data.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Logging Files](#logging-files)
- [Honeypot Types](#honeypot-types)
- [Dashboard](#dashboard)
- [Helpful Resources](#helpful-resources)

## Installation

To run the honeypot locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Its-Abood/baitbot.git
   cd baitbot

2. **Install the dependencies:**
Ensure you have Python 3 installed. Install the required packages:

    `pip install -r requirements.txt`

3. **Generate RSA Key:**
For the SSH honeypot, you'll need an RSA key for simulating SSH connections. You can generate one by running the following command in the main directory:

    `ssh-keygen -t rsa -b 2048 -f server.key`

This will generate `server.key` (private key) and `server.key.pub` (public key) in your honeypot directory.

4. **Set file permissions:**
Ensure your main honeypot script is proper:

    `chmod 755 ssh_honeypot.py web_honeypot.py honeypot.py`

5. **Adjust the SSH port:**

    By default, SSH operates on port 22. You can change this to any port, such as 2223, by editing the configuration file or running the script with a custom port:

## Usage

To provision a new instance of HONEYPY, use the `honeypot.py` file. This is the main file to interface with for HONEYPY. 

HONEYPY requires a bind IP address (`-a`) and network port to listen on (`-p`). Use `0.0.0.0` to listen on all network interfaces. The protocol type must also be defined.

```
-a / --address: Bind address.
-p / --port: Port.
-s / --ssh / --http: Declare honeypot type.
```

Example: `python3 honeypot.py -a 0.0.0.0 -p 2223 --ssh`

also u can start the `honeypot` by:

**SSH Honeypot:**

`python3 ssh_honeypot.py`

This will run the SSH honeypot on your specified port (default is 22, or whatever you set).

**Or Web Honeypot:**

`python3 web_honeypot.py`

This will run a Flask web app simulating a login page.

**Testing**

You can test the SSH honeypot by attempting to connect via SSH on the port you configured (e.g., 2223):

`ssh username@localhost -p 2223`

For the web honeypot, open a browser and go to:

`http://localhost:5000`

## Logging Files

All connection attempts are logged in the following locations:

**SSH Logs:** `audits.log`

**Commands excuted:** `cmd_audits.log`

**Web Honeypot Logs:** `honeypot_web.log`

These logs record details like IP address, attempted credentials, and timestamps.

## Honeypot Types

**What is a Honeypot?**

A honeypot is a security mechanism designed to lure and trap attackers by simulating vulnerable systems or services. There are two main types in this project:

**SSH Honeypot:** Emulates an SSH service and logs brute-force attempts.

**Web Honeypot:** Simulates a login page and captures attempted logins.

## Dashboard

The project includes a simple dashboard to monitor login attempts in real-time. After running the web honeypot, you can view it by visiting:

`http://localhost:5000/dashboard`

This shows recent SSH and web login attempts with their details.

## Helpful Resources
**These are some of the resources and guides used while developing this project:**

-   https://gist.github.com/cschwede/3e2c025408ab4af531651098331cce45
-   https://owasp.org/www-project-honeypot/
-   https://flask.palletsprojects.com/en/3.0.x/tutorial/factory/
-   https://www.ibm.com/docs/en/ahts/4.4.x?topic=iu-configuring-ssh-server-3
