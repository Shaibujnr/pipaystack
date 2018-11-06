import json
import requests
import enum


class SingletonMeta(type):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)

        cls.__instance = None
        original_new = cls.__new__

        def meta_new(cls, *args, **kwargs):
            if not cls.__instance:
                cls_obj = original_new(cls, *args, **kwargs)
                cls.__instance = cls_obj
            return cls.__instance

        # replace `__new__` method
        cls.__new__ = staticmethod(meta_new)


class TransactionStatus(enum.Enum):
    SUCCESS = 1
    FAILED = 2
    ABANDONED = 3


    @classmethod
    def from_string(cls, status_string):
        status_string_mapping = {
            'success': cls.SUCCESS,
            'failed': cls.FAILED,
            'abandoned': cls.ABANDONED
        }
        return status_string_mapping[status_string]

    
    def __str__(self):
        if self == self.SUCCESS:
            return 'success'
        if self == self.FAILED:
            return 'failed'
        if self == self.ABANDONED:
            return 'abandoned'


class Paystack(metaclass=SingletonMeta):
    __secret = None
    __requests = None

    def __init__(self, secret=None):
        if not secret and not self.__class__.__secret:
            raise Exception("Paystack has not been initialized before")
        if self.__class__.__secret and not secret:
            return
        self.__class__.__secret = secret
        self.secret = self.__class__.__secret
        self.requests = self.getRequest()
        self.root_url = "https://api.paystack.co"
       

    def __new__(cls, secret=None):
        return super(Paystack, cls).__new__(cls)


    def getRequest(self):
        sr = requests.Session()
        sr.headers.update(
            {
                'Authorization': 'Bearer {0}'.format(self.secret),
                'Content-Type': "application/json"
            }
        )
        return sr


class Transaction:
    def __init__(self, reference=None):
        self.amount = None
        self.message = None
        self.id = None
        self.status = None
        self.metadata = None
        self.ip = None
        self.channel = None
        self.reference = reference
        self.customer = None
        self.authorization = None
        self.paid_at = None
        self.created_at = None
        self.authorization_url = None
        self.access_code = None

    
    def verify(self):
        ps = Paystack()
        r = ps.requests
        response = r.get('{0}//transaction/verify/{1}'.format(ps.root_url,self.reference))
        if response.status_code == 200:
            rjson = response.json()
            tdata = rjson.get('data')
            self.__from_json(tdata, self)
            return self.status
            

    @classmethod
    def initialize(cls, email, amount, reference=None, metadata=None, channels=None, callback_url=None):
        amount = str(amount * 100)
        args = locals()
        ps = Paystack()
        r = ps.requests
        post_data = {k:v for k,v in args.items() if v is not None and k != "cls"}
        response = r.post("{0}/transaction/initialize".format(ps.root_url), data=json.dumps(post_data))
        if response.status_code == 200:
            rjson = response.json()
            transaction_data = rjson.get("data")
            transaction = Transaction()
            transaction.message = rjson.get("message")
            transaction.metadata = metadata
            transaction.reference = transaction_data.get("reference")
            transaction.authorization_url = transaction_data.get("authorization_url")
            transaction.access_code = transaction_data.get("access_code")
            return transaction
        else:
            print(response.status_code)
            print(response.text)
            print(post_data)
            raise Exception("Incorrect transaction details")


    @classmethod
    def fetch(self, per_page=None, page=None, customer_id=None, status=None, amount=None, from_date=None, to_date=None):
        transactions = []
        amount = amount * 100 if amount else None
        ps = Paystack()
        r = ps.requests
        params = {
            "perPage": per_page, 
            "page":page, 
            "customer":customer_id, 
            "status":status,
            "amount": amount,
            "from": from_date,
            "to": to_date 
        }
        params = {k:v for k,v in params.items() if v is not None}
        response = r.get("{0}/transaction".format(ps.root_url), params=params)
        if response.status_code == 200:
            rjson = response.json()
            transactions_data = rjson.get('data')
            for t in transactions_data:
                transactions.append(self.__from_json(t))
        return transactions


    @classmethod
    def get(cls, transaction_id):
        ps = Paystack()
        r = ps.requests
        response = r.get("{0}/transaction/{1}".format(ps.root_url,transaction_id))
        if response.status_code == 200:
            rjson = response.json()
            transaction_data = rjson.get('data')
            transaction = cls.__from_json(transaction_data)
            return transaction


    @staticmethod
    def __from_json(jdict, instance=None):
        t = Transaction() if not instance else instance
        t.id = jdict.get('id')
        t.status = TransactionStatus.from_string(jdict.get('status'))
        t.amount = jdict.get('amount')
        t.reference = jdict.get('reference')
        t.message = jdict.get('message')
        t.channel = jdict.get('channel')
        t.metadata = jdict.get('metadata')
        t.ip = jdict.get('ip_address').split(",")
        t.created_at = jdict.get('created_at')
        t.paid_at = jdict.get('paid_at')
        return t

class Charge:
    pass

class Customer:
    pass

class TransferReceipient:
    pass

class Transfer:
    pass