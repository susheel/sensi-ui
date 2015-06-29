import os
from flask import Flask, render_template, request
import paramiko
from subprocess import Popen, PIPE
from subprocess import call

from settings import credentials

SENSI_HOST = os.getenv('SENSI_HOST', "0.0.0.0")
SENSI_PORT = os.getenv('SENSI_PORT', 8080)

CMD_STR = "echo '{parameters}' > {workfolder}/{model}_parameters.txt && {script} {model} {workfolder}/{model}_parameters.txt {samples} {inputs} {outputs}"

app = Flask(__name__, static_folder = "./static")

@app.route("/")
def index():
  return render_template('index.html')

@app.route("/ishigami")
def ishigami():
  return render_template('ishigami.html')

@app.route("/zeroVFFR")
def zeroVFFR():
  return render_template('zerovffr.html')

@app.route("/oneVFFR")
def oneVFFR():
  return render_template('oneVFFR.html')

@app.route("/submit", methods=['POST'])
def submit():
  params = {
    'model' : request.form['model'],
    'samples': request.form['samples'],
    'parameters' : request.form['parameters'],
    'inputs' : request.form['inputs'],
    'outputs' : request.form['outputs'],
    'location' : request.form['location'],
    'script' : request.form['script'],
    'workfolder' : request.form['workfolder']
  }
  error, logs = submit_ssh_command(params)
  print error, logs
  if error:
    return render_template('error.html', logs=logs, params=params)
  else:
    return render_template('success.html', logs=logs, params=params)

# def submit_ssh_command(params):
#   error = False
#   logs = []
#   i = 1
#   while True:
#     logs.append("Trying to connect to %s (%i/3)" % (params['location'], i))

#     try:
#       ssh = paramiko.SSHClient()
#       ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#       host = credentials[params['location']]['host']
#       user = credentials[params['location']]['username']
#       passwd = credentials[params['location']]['password']

#       ssh.connect(host, username=user, password=passwd, timeout=5.0)

#       logs.append("Connected to %s" % params['location'])
#       break
#     except paramiko.AuthenticationException:
#       error = True
#       logs.append("Authentication failed when connecting to %s" % params['location'])
#     except:
#       logs.append("Could not SSH to %s, waiting for it to start" % params['location'])
#       i += 1
#       time.sleep(2)

#     if i == 3:
#       error = True
#       logs.append("Could not connect to %s. Giving up" % params['location'])

#   stdin, stdout, stderr = ssh.exec_command('ls')

#   while not stdout.channel.exit_status_ready():
#     if stdout.channel.recv_ready():
#       logs.extend(stdout.readlines())

#   ssh.close()

#   return error, logs

def generate_cmd_string(params):
  return CMD_STR.format(script=params['script'],
      model=params['model'],
      samples=params['samples'],
      parameters=params['parameters'],
      inputs=params['inputs'],
      outputs=params['outputs'],
      workfolder=params['workfolder'])

def submit_ssh_command(params):

  error = False
  logs = []
  logs.append("Trying to connect to %s..." % params['location'])
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host = credentials[params['location']]['host']
    user = credentials[params['location']]['username']
    passwd = credentials[params['location']]['password']

    ssh.connect(host, username=user, password=passwd, timeout=5.0)
    logs.append("Connected to %s..." % params['location'])

    logs.append("Submitting Sensi Job to %s..." % params['location'])
    command = generate_cmd_string(params)
    stdin, stdout, stderr = ssh.exec_command(command)
    logs.append("Result of command %s is:" % command)

    while not stdout.channel.exit_status_ready():
       if stdout.channel.recv_ready():
        logs.extend(stdout.readlines())

  except paramiko.AuthenticationException:
    error = True
    logs.append("Authentication failed when connecting to %s." % params['location'])
  except:
    error = True
    logs.append("Could not SSH to %s." % params['location'])

  ssh.close()

  return error, logs

# wait for VPN to be properly up ...
# while True:
#     p = Popen(["/webapp/sensi-ui/configvpn"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
#     output, err = p.communicate()
#     p = Popen(["route", "-n"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
#     output, err = p.communicate()
#     if output.count("ppp0")==2 and output.count("eth0")>=2:
#         break
#     time.sleep(5)


if __name__ == "__main__":
    app.run(host=SENSI_HOST, port=SENSI_PORT, debug=True)

