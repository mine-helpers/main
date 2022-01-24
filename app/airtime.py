import random

class DonationTime():
    def luhn_residue(self,digits):
        return sum(sum(divmod(int(d)*(1 + i%2), 10)) for i, d in enumerate(digits[::-1])) % 10
    
    def getImei(self,N):
        part = ''.join(str(random.randrange(0,9)) for _ in range(N-1))
        res = self.luhn_residue('{}{}'.format(part, 0))
        return '{}{}'.format(part, -res%10)