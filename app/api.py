from flask import current_app
import pyotp


class kfp_otp():
    SECRET = 'DPBXBWP3WDX5VUI5'
    hotp = pyotp.HOTP(SECRET)

    def generate_otp(self,phone_number):
        otp =  self.hotp.at(int(phone_number))
        return int(otp)

    def verify_otp(self,otp,phone_number):
        flag = self.hotp.verify(int(otp),int(phone_number))
        return flag
        