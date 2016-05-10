#!/usr/bin/env python2.7


import os
import boto
import boto.dynamodb2
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.items import Item
import time
from dateutil.parser import parse
from flask import Flask, session, url_for, flash, request, render_template, g, redirect, Response
from contextlib import closing
DEBUG = True
SECRET_KEY = 'development key'

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config.from_object(__name__)

#You should use your own account information.
ACCOUNT_ID ='YOUR ACCOUNT_ID' 
IDENTITY_POOL_ID ='YOUR IDENTITY_POOL_ID'
ROLE_ARN = 'YOUR ROLE_ARN'


cognito = boto.connect_cognito_identity()
cognito_id = cognito.get_id(ACCOUNT_ID, IDENTITY_POOL_ID)
oidc = cognito.get_open_id_token(cognito_id['IdentityId'])

sts = boto.connect_sts()
assumedRoleObject = sts.assume_role_with_web_identity(ROLE_ARN,"XX",oidc['Token'])

client_dynamo = boto.dynamodb2.connect_to_region('us-east-1',aws_access_key_id=assumedRoleObject.credentials.access_key,aws_secret_access_key=assumedRoleObject.credentials.secret_key,security_token=assumedRoleObject.credentials.session_token)

if (not Table('IOTproject',connection=client_dynamo)):
    mytable =Table.create('IOTproject',schema=[HashKey('id')],connection=client_dynamo)
    time.sleep(20)
mytable = Table('IOTproject',connection=client_dynamo)




@app.before_request
def before_request():
  pass

@app.teardown_request
def teardown_request(exception):
  pass

@app.route('/', methods=['POST','GET'])
def index():
  num = None
  """
  alldata = mytable.scan()
  for data in alldata:
    print data['time']
  """
  recent = mytable.query_2(id__eq=1,limit = 1,reverse = True)
  for data in recent:
    num = data['NumberOfFaces']
    print num
    print data['time']
  seats = dict(a=data['Seat 1'],b=data['Seat 2'],c=data['Seat 3'],d=data['Seat 4'])
  print seats
  return render_template("index.html",num = num, seats = seats)



if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=threaded)

  run()
