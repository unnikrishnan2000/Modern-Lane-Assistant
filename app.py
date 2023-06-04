
from urllib import request
from flask import Flask,render_template,request,send_file,jsonify

import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import tensorflow as tf
from keras import applications  
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model

from datetime import datetime 

import calendar;
import time;
 
# gmt stores current gmtime
gmt = time.gmtime()
print("gmt:-", gmt)
 
# ts stores timestamp
ts = calendar.timegm(gmt)
print("timestamp:-", ts)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'images'


@app.route('/',methods=['GET'])
def home():
    #imagefile=request.files['imagefile']
    #image_path = "./images/" + imagefile.filename
    #imagefile.save(image_path)
       
        
    return render_template("index.html")



@app.route('/image')
def get_image():
    # Retrieve the image path from the query string
    image_path = request.args.get('path')

    # Send the image file to the client's browser
    return send_file(image_path, mimetype='image/jpg')


@app.route('/live')
def live():
    os.system("python yolov5/detect.py --weights yolov5/runs/train/exp/weights/best.pt --source 0")
    return render_template("index.html") 

@app.route('/predict',methods=['POST'])
def predict():
    name2= str(datetime.now().year) + str(datetime.now().month) + str(datetime.now().day)+'-'+str(datetime.now().hour)+str(datetime.now().minute)+str(datetime.now().second)
    name=name2+'.jpg'
    photo = request.files['image']
    path = os.path.join(app.config['UPLOAD_FOLDER'],name)
    photo.save(path)

    command="python yolov5/detect.py --weights yolov5/runs/train/exp/weights/best.pt --source "+path+" --save-txt --exist-ok --line-thickness=2"
    print(command)


    os.system(command)  

    labelname="yolov5/runs/detect/exp/labels/"+name2+".txt"
    imagepath="yolov5/runs/detect/exp/"+name2+".jpg"


    with open(labelname, "r") as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]
    temp=[]
    for line in lines:
        temp.append(list(line.split(" ")))

    detected_class=[]
    for line in lines:
        detected_class.append(int(line.split()[0]))
    name= ['ambulance', 'army vehicle', 'auto rickshaw', 'bicycle', 'bus', 'car', 'garbagevan', 'human hauler', 'minibus', 'minivan', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'truck', 'van', 'wheelbarrow']
    # print(detected_class)
    lst=[]

    emergency=0

    for val in detected_class:
        lst.append(name[int(val)])
    # return lst

    if 0 in detected_class:
        speed=5
        distance=20
        lane=3
        t=distance/speed
        tme=len(lst)*(t/lane)
        tmin=15
        tmax=60
        color="green"
        countdown=-100
        return render_template("result.html",imgpth=imagepath,count=len(lst),time=int(tme),color=color,c=countdown)
    else:
        speed=5
        distance=20
        lane=3
        t=distance/speed
        tme=len(lst)*(t/lane)
        tmin=15
        tmax=60
        if tme<tmin:
            color="red"
            countdown=-1
        elif tme<tmax:
            color="green"
            countdown=tme
        else:
            color="green"
            countdown=tmax
        print(countdown)
        return render_template("result.html",imgpth=imagepath,count=len(lst),time=int(tme),color=color,c=countdown)
        


if __name__ =='__main__':
    app.run(port=3000, debug=True)