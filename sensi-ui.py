import os
from flask import Flask, render_template, request
import paramiko

from settings import credentials

SENSI_HOST = os.getenv('SENSI_HOST', "0.0.0.0")
SENSI_PORT = os.getenv('SENSI_PORT', 8080)

CMD_STR = "{script} {samples} "

app = Flask(__name__)

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
    'script' : request.form['script']
  }
  error, logs = submit_ssh_command(params)
  print error, logs
  if error:
    return render_template('error.html', logs=''.join(logs))
  else:
    return render_template('success.html', logs=''.join(logs))

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

def submit_ssh_command(params):

  error = False
  logs = []
  logs.append("Trying to connect to %s" % params['location'])
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    host = credentials[params['location']]['host']
    user = credentials[params['location']]['username']
    passwd = credentials[params['location']]['password']

    ssh.connect(host, username=user, password=passwd, timeout=5.0)
    logs.append("Connected to %s" % params['location'])
  except paramiko.AuthenticationException:
    error = True
    logs.append("Authentication failed when connecting to %s" % params['location'])
  except:
    logs.append("Could not SSH to %s" % params['location'])

  logs.append("Submitting Sensi Job to %s" % params['location'])
  stdin, stdout, stderr = ssh.exec_command('ls')

  while not stdout.channel.exit_status_ready():
    if stdout.channel.recv_ready():
      logs.extend(stdout.readlines())

  ssh.close()

  return error, logs



if __name__ == "__main__":
    app.run(host=SENSI_HOST, port=SENSI_PORT, debug=True)

