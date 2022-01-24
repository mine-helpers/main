import requests
from .models import Message, Log
from . import db
import json

def send_sms():
    pass

class SMSApi():
    API_URL = 'https://sms.a23.us/api/v2.0/send/sms'
    API_KEY = '4f312a0a8cbc41ba90ac9c254044efed'

    def send_sms(self,to,message):
        payload={
            'key': self.API_KEY,
            'to': to,
            'message': message
        }

        r = requests.get(self.API_URL,params=payload)
        print(r.text)
        if r.status_code == requests.codes.ok:
            res = r.json()
            sms = Message(phone_number=res['to'],
                          status=res['status'],
                          unique_id=res['unique_id'],
                          response=r.text,body=res['sms'])
            db.session.add(sms)
            return r.status_code

        elif r.status_code == 400:
            res = r.json()
            error = res['error']
            log = Log(body=r.text,error='Bad request made to the sms service',
                     error_code=r.status_code) 
            db.session.add(log)          
            return r.status_code

        elif r.status_code == 500:
            log = Log(body=r.text,error='Internal server error from the sms service',
                     error_code=r.status_code)
            db.session.add(log)
            return r.status_code

        elif r.status_code == 502:
            log = Log(body=r.text,error='Bad gateway returned from Nginx to the SMS Service',
                     error_code=r.status_code)
            db.session.add(log)
            return r.status_code

