#!/usr/bin/python
import boto
import boto.dynamodb2
from boto.dynamodb2.table import Table
from boto.dynamodb2.types import NUMBER
from boto.dynamodb2.fields import HashKey, RangeKey
from boto.dynamodb2.items import Item
import time
import cv2
import numpy as np
import time
import sys
#sys.path.append('/usr/local/Cellar/opencv/2.4.12_2/lib/python2.7/site-packages')

ACCOUNT_ID =' '
IDENTITY_POOL_ID =' '
ROLE_ARN = ' '

# Use cognito to get an identity.
cognito = boto.connect_cognito_identity()
cognito_id = cognito.get_id(ACCOUNT_ID, IDENTITY_POOL_ID)
oidc = cognito.get_open_id_token(cognito_id['IdentityId'])

# Further setup your STS using the code below
sts = boto.connect_sts()
assumedRoleObject = sts.assume_role_with_web_identity(ROLE_ARN,"XX",oidc['Token'])

client_dynamo = boto.dynamodb2.connect_to_region(
    'us-east-1',
    aws_access_key_id=assumedRoleObject.credentials.access_key,
    aws_secret_access_key=assumedRoleObject.credentials.secret_key,
    security_token=assumedRoleObject.credentials.session_token)

DYNAMODB_TABLE_NAME = 'IOTproject'
table_exists=False
try:
	tabledescription = client_dynamo.describe_table(DYNAMODB_TABLE_NAME)
	table_exists = True
except Exception as e:
	if "Requested resource not found: Table" in str(e):
		table_exists = False

if not table_exists:
	table = Table.create(DYNAMODB_TABLE_NAME, schema=[HashKey('id', data_type = NUMBER),RangeKey('time', data_type = NUMBER)], connection=client_dynamo)
	time.sleep(20)
else:
	table=Table(DYNAMODB_TABLE_NAME,connection=client_dynamo)



cap=cv2.VideoCapture(0)
cascPath = '/path-to-the-classifier/cascades.xml'
classifier=cv2.CascadeClassifier(cascPath)
time.sleep(1)

# the detection result of the four seats
seat1 = []
seat2 = []
seat3 = []
seat4 = []

try:
    while True:
        success,frame=cap.read()
        size=frame.shape[:2]
        image=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        divisor=15
        h,w=size

        # 4 rectangles to dicide whether there are peple in these spots
        cv2.rectangle(frame,(w/20*8,h/20),(w/20*12,h/20*7),(0,0,255),1)
        cv2.putText(frame,"seat 1",(w/20*10,h/20*4),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
        cv2.rectangle(frame,(w/20*8,h/20*13),(w/20*12,h/20*19),(0,0,255),1)
        cv2.putText(frame,"seat 2",(w/20*10,h/20*16),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
        cv2.rectangle(frame,(w/20*2,h/20*7),(w/20*6,h/20*13),(0,0,255),1)
        cv2.putText(frame,"seat 3",(w/20*4,h/20*10),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
        cv2.rectangle(frame,(w/20*14,h/20*7),(w/20*18,h/20*13),(0,0,255),1)
        cv2.putText(frame,"seat 4",(w/20*16,h/20*10),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)

        # store the 10 most recent detections
        if len(seat1) >= 10 :
            seat1.pop(0)
        if len(seat2) >= 10 :
            seat2.pop(0)
        if len(seat3) >= 10 :
            seat3.pop(0)
        if len(seat4) >= 10 :
            seat4.pop(0)

        num_people = 0
        faceRects=classifier.detectMultiScale(image,scaleFactor=1.1,minNeighbors=3,flags=cv2.CASCADE_SCALE_IMAGE,minSize=(w/divisor,h/divisor))
        if len(faceRects)>0:
            for faceRect in faceRects:
                x,y,w1,h1=faceRect
                center1 = x + w1 * 0.5
                center2 = y + h1 * 0.5
                # seat 1
                if (center1 >= w/20*8 and center1 <= w/20*12 and center2 >= h/20 and center2 <= h/20*7):
                    num_people = num_people + 1
                    cv2.rectangle(frame,(w/20*8,h/20),(w/20*12,h/20*7),(255,0,0),1)
                    cv2.putText(frame,"seat 1",(w/20*10,h/20*4),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
                    seat1.append(1)
                else:
                    seat1.append(0)
                # seat 2
                if (center1 >= w/20*8 and center1 <= w/20*12 and center2 >= h/20*13 and center2 <= h/20*19):
                    num_people = num_people + 1
                    cv2.rectangle(frame,(w/20*8,h/20*13),(w/20*12,h/20*19),(255,0,0),1)
                    cv2.putText(frame,"seat 2",(w/20*10,h/20*16),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
                    seat2.append(1)
                else:
                    seat2.append(0)
                # seat 3
                if (center1 >= w/20*2 and center1 <= w/20*6 and center2 >= h/20*7 and center2 <= h/20*13):
                    num_people = num_people + 1
                    cv2.rectangle(frame,(w/20*2,h/20*7),(w/20*6,h/20*13),(255,0,0),1)
                    cv2.putText(frame,"seat 3",(w/20*4,h/20*10),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
                    seat3.append(1)
                else:
                    seat3.append(0)
                # seat 4
                if (center1 >= w/20*14 and center1 <= w/20*18 and center2 >= h/20*7 and center2 <= h/20*13):
                    num_people = num_people + 1
                    cv2.rectangle(frame,(w/20*14,h/20*7),(w/20*18,h/20*13),(255,0,0),1)
                    cv2.putText(frame,"seat 4",(w/20*16,h/20*10),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
                    seat4.append(1)
                else:
                    seat4.append(0)
                cv2.rectangle(frame,(x,y),(x+w1,y+h1),(0,255,0),2)
        else:
            seat1.append(0)
            seat2.append(0)
            seat3.append(0)
            seat4.append(0)

        print "Find {0} person(s)".format(num_people)
        # seat1 upload value
        seat1_sort = sorted(seat1)
        seat1_sort.sort()
        seat1_up = seat1_sort[len(seat1_sort)/2]
        # seat2 upload value
        seat2_sort = sorted(seat2)
        seat2_sort.sort()
        seat2_up = seat2_sort[len(seat2_sort)/2]
        # seat3 upload value
        seat3_sort = sorted(seat3)
        seat3_sort.sort()
        seat3_up = seat3_sort[len(seat3_sort)/2]
        # seat4 upload value
        seat4_sort = sorted(seat4)
        seat4_sort.sort()
        seat4_up = seat4_sort[len(seat4_sort)/2]

        number = seat1_up + seat2_up + seat3_up + seat4_up
        cv2.putText(frame,"{0} people(s)".format(number),(w/20*15,h/20*18),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),1)
        cv2.putText(frame,"The median of",(w/20*14,h/20*19),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),1)
        cv2.putText(frame,"10 recent detection",(w/20*14,h/40*39),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),1)
        cv2.imshow("test",frame)

        ts = int(time.time())
        newItem = Item(table,data={'id':1,'time':ts,'NumberOfFaces':number,'Seat 1':seat1_up,'Seat 2':seat2_up,'Seat 3':seat3_up,'Seat 4':seat4_up})
        newItem.save()
        if cv2.waitKey(1) &0xFF == ord('q'):
            break
        time.sleep(1)
except Exception,e:
    print e
    cap.release()
cap.release()
