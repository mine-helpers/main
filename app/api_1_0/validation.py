def isEmpty(errors):
    if type(errors) == dict:
        if len(errors.values()) == 0:
            return True
        else:
            return False
    else:
        raise ValueError('errors must be a dictionary')

def isStrEmpty(param):
    if len(param) == 0:
        return True
    return False


def verify_phonenumber(phone_number):
    if len(phone_number) != 12:
        return False
    for i in range(12):
        if not phone_number[i].isdigit():
            return False
    return True

def verify_code(phone_number):
    if len(phone_number) != 6:
        return False
    for i in range(6):
        if not phone_number[i].isdigit():
            return False
    return True