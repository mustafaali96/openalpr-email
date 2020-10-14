#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from datetime import datetime
from database import db_insert, db_get_loc
import json
import wget
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

port = 587  # For starttls
smtp_server = "smtp.gmail.com"
sender_email = "sender@mail.com"
receiver_email = "receiver@mail.com"
password = "" #input("Type your password and press enter:")

msg = MIMEMultipart()
msg['Subject'] = 'Open ALPR Vehicle Details'
msg['From'] = sender_email
msg['To'] = receiver_email 

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        new_post_data = post_data.decode('utf-8').replace("'", '"')
 
        data = json.loads(new_post_data)
        
        try:
            result = data['best_plate']
            plate_crop = "localhost:8356/crop/" + str(data['best_uuid']) + ".jpg?x1=" + str(result["coordinates"][0]['x']) + "&y1=" + str(result["coordinates"][0]['y']) +"&x2=" + str(result["coordinates"][2]['x']) + "&y2=" + str(result["coordinates"][2]['y'])
            
            x_w = int(result["vehicle_region"]['x']) + int(result["vehicle_region"]['width'])
            y_h = int(result["vehicle_region"]['y']) + int(result["vehicle_region"]['height'])
            
            global car_crop
            car_crop = "http://localhost:8356/crop/" + str(data['best_uuid']) + ".jpg?x1=" + str(result["vehicle_region"]['x']) + "&y1=" + str(result["vehicle_region"]['y']) +"&x2=" + str(x_w) + "&y2=" + str(y_h) + ".jpg"
            print("car crop: ",car_crop)
            
            print('camera id',data['camera_id'])
            print('confidence',data['best_confidence'])
            
            #confidence = data['best_confidence']
            camera_id = data['camera_id']
            global plate
            plate= "\nPlate number is" + data['best_plate_number']
            global uid
            uid = data['best_uuid']
            print(plate)
            print("UID is: ", uid)
            global date_time
            date_time = "\nDate and Time" + str(datetime.now())
            print(date_time)
            s = json.dumps(data, indent=4, sort_keys=True)
            
            loc = db_get_loc(camera_id)
            db_insert(plate,uid,camera_id,date_time,plate_crop,car_crop,loc)
            
#            image = wget.download(car_crop)
#            msg = """\
#            Subject: Open ALPR Vehicle Detail 
#            """ + plate + date_time + """ \nThis is an automated generated email from Xclusive Open ALPR System."""
#            
#            #context = ssl.create_default_context()
#            #image = str(uid) + ".jpg"
#            with open(image, 'rb') as fp:
#                img = MIMEImage(fp.read())
#                img.add_header('Content-Disposition', 'attachment', filename=image)
#                msg.attach(img)
#            with smtplib.SMTP(smtp_server, port) as server:
#                server.ehlo()  # Can be omitted
#                server.starttls()
#                server.ehlo()  # Can be omitted
#                server.login(sender_email, password)
#                server.sendmail(sender_email, receiver_email, msg)
#                print("Email sent")
        
        except:
            pass
#        
        finally:
            image = wget.download(car_crop)
            msgText = MIMEText(str(plate) + str(date_time), 'html')
            msg.attach(msgText)
#            msg = """\
#            Subject: Open ALPR Vehicle Detail 
#            """ + plate + date_time + """ \nThis is an automated generated email from Xclusive Open ALPR System."""
            
            #context = ssl.create_default_context()
            #image = str(uid) + ".jpg"
#            with open(image, 'rb') as fp:
#                img = MIMEImage(fp.read())
#                fp.close()
#                img.add_header('Content-Disposition', 'attachment', filename=image)
#                msg.attach(img)
            with open(image, 'rb') as fp:
                img = MIMEImage(fp.read())
                img.add_header('Content-Disposition', 'attachment', filename=image)
                msg.attach(img)
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()  # Can be omitted
                server.starttls()
                server.ehlo()  # Can be omitted
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                print("Email sent")
        
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        
        


def run(server_class=HTTPServer, handler_class=S, port=8081):
    logging.basicConfig(level=logging.INFO)
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()