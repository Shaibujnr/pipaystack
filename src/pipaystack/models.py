import json
import requests
from .enum import TransactionStatus, ChargeType


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
        if response.json().get('data'):
            rjson = response.json()
            tdata = rjson.get('data')
            self.__from_json(tdata, self)
            return self.status
            
            
    def authorize_pin(self, pin):
            ps = Paystack()
            r = ps.requests
            endpoint = "{0}/charge/submit_pin".format(ps.root_url)
            post_data = {'pin':pin, 'reference': self.reference}
            response = r.post(endpoint, data=json.dumps(post_data))
            if response.json().get('data'):
                rjson = response.json()
                data = rjson.get('data')
                status = TransactionStatus.from_string(data.get('status'))
                self.status = status
            elif not response.json().get('status'):
                print('\nfrom authorize pin\n')
                print(self.reference)
                print(response.text)


    def authorize_otp(self, otp):
        ps = Paystack()
        r = ps.requests
        endpoint = "{0}/charge/submit_otp".format(ps.root_url)
        post_data = {'otp':otp, 'reference': self.reference}
        response = r.post(endpoint, data=json.dumps(post_data))
        if response.json().get('data'):
            rjson = response.json()
            data = rjson.get('data')
            status = TransactionStatus.from_string(data.get('status'))
            self.status = status
        elif not response.json().get('status'):
            print('\nfrom authorize otp\n')
            print(self.reference)
            print(response.text)


    def authorize_phone(self, phone):
        ps = Paystack()
        r = ps.requests
        endpoint = "{0}/charge/submit_phone".format(ps.root_url)
        post_data = {'phone':phone, 'reference': self.reference}
        response = r.post(endpoint, data=json.dumps(post_data))
        if response.json().get('data'):
            rjson = response.json()
            data = rjson.get('data')
            status = TransactionStatus.from_string(data.get('status'))
            self.status = status
        elif not response.json().get('status'):
            print('\nfrom authorize phone\n')
            print(self.reference)
            print(response.text)


    def authorize_birthday(self, birthday):
        ps = Paystack()
        r = ps.requests
        endpoint = "{0}/charge/submit_birthday".format(ps.root_url)
        post_data = {'birthday':birthday, 'reference': self.reference}
        response = r.post(endpoint, data=json.dumps(post_data))
        if response.json().get('data'):
            rjson = response.json()
            data = rjson.get('data')
            status = TransactionStatus.from_string(data.get('status'))
            self.status = status
        elif not response.json().get('status'):
            print('\nfrom authorize birthday\n')
            print(self.reference)
            print(response.text)


    @classmethod
    def initialize(cls, email, amount, reference=None, channels=None, callback_url=None, **metadata):
        amount = str(amount * 100)
        args = locals()
        ps = Paystack()
        r = ps.requests
        post_data = {k:v for k,v in args.items() if bool(v) and k != "cls"}
        response = r.post("{0}/transaction/initialize".format(ps.root_url), data=json.dumps(post_data))
        if response.json().get('data'):
            rjson = response.json()
            transaction_data = rjson.get("data")
            transaction = Transaction()
            transaction.message = rjson.get("message")
            transaction.metadata = metadata if bool(metadata) else None
            transaction.reference = transaction_data.get("reference")
            transaction.authorization_url = transaction_data.get("authorization_url")
            transaction.access_code = transaction_data.get("access_code")
            return transaction
        elif not response.json().get('status'):
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
        if response.json().get('data'):
            rjson = response.json()
            transactions_data = rjson.get('data')
            for t in transactions_data:
                transactions.append(self.__from_json(t))
        elif not response.json().get('status'):
            print('\nfrom transaction fetch\n')
            print(response.text)
        
        return transactions


    @classmethod
    def get(cls, transaction_id):
        ps = Paystack()
        r = ps.requests
        response = r.get("{0}/transaction/{1}".format(ps.root_url,transaction_id))
        if response.json().get('data'):
            rjson = response.json()
            transaction_data = rjson.get('data')
            transaction = cls.__from_json(transaction_data)
            return transaction
        elif not response.json().get('status'):
            print('\nfrom transaction get\n')
            print(response.text)


    @classmethod
    def charge(cls, charge_type, email, amount):
        amount = str(amount*100)
        ps = Paystack()
        r = ps.requests
        endpoint = "{0}/charge".format(ps.root_url)

        def __start_card_charge(number, cvv, expiry_month, expiry_year, reference=None, **metadata):
            post_data = {
                "email": email,
                "amount": amount,
                "metadata": metadata,
                "card": {
                    'cvv':cvv,
                    'number':number,
                    'expiry_month':expiry_month,
                    'expiry_year':expiry_year
                }
            }
            if reference: post_data['reference'] = reference
            response = r.post(endpoint, data=json.dumps(post_data))
            if response.json().get('data'):
                rjson = response.json()
                data = rjson.get('data')
                t = Transaction(data.get('reference'))
                t.status = TransactionStatus.from_string(data.get('status'))
                return t
            elif not response.json().get('status'):
                print('\nfrom start card charge\n')
                print(response.text)


        def __start_bank_charge(bank, account_number, bank_code=None, reference=None, **metadata):
            code = bank_code or bank.value
            post_data = {
                "email": email,
                "amount": amount,
                "metadata": metadata,
                "bank": {
                    'code':code,
                    'account_number':account_number
                }
            }
            if reference: post_data['reference'] = reference
            response = r.post(endpoint, data=json.dumps(post_data))
            if response.json().get('data'):
                rjson = response.json()
                data = rjson.get('data')
                t = Transaction(data.get('reference'))
                t.status = TransactionStatus.from_string(data.get('status'))
                return t
            elif not response.json().get('status'):
                print('\nfrom start bank charge\n')
                print(response.text)

        __chargetype_func_mapping = {ChargeType.CARD: __start_card_charge, ChargeType.BANK: __start_bank_charge}
        return type("__Charge", (), {'start': __chargetype_func_mapping[charge_type]})


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


class Customer:
    def __init__(self, email, first_name=None, last_name=None, phone=None, **metadata):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.metadata = metadata
        self.code = None
        self.id = None
        self.integration = None
        self.subscriptions = []
        self.authorizations = []
        self.created_at = None
        self.updated_at = None


    @property
    def transactions(self):
        return Transaction.fetch(customer_id=self.id)

    
    def create(self):
        ps = Paystack()
        r = ps.requests
        post_data = {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'metadata': self.metadata
        }
        post_data = {k:v for k,v in post_data.items() if bool(v)}
        response = r.post('{0}/customer'.format(ps.root_url), data=json.dumps(post_data))
        if response.status_code == 200 and response.json().get('status'):
            rjson = response.json()
            customer_data = rjson.get('data')
            self.integration = customer_data.get('integration')
            self.code = customer_data.get('customer_code')
            self.id = customer_data.get('id')
            self.created_at = customer_data.get('createdAt')
            self.updated_at = customer_data.get('updatedAt')
            return "Customer Created"


    def update(self, first_name=None, last_name=None, phone=None, **metadata):
        if not self.id:
            raise Exception("Customer has not been created")
        ps = Paystack()
        r = ps.requests
        put_data = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'metadata': metadata
        }
        put_data = {k:v for k,v in put_data.items() if bool(v)}
        response = r.put('{0}/customer/{1}'.format(ps.root_url, self.id), data=json.dumps(put_data))
        if response.status_code == 200 and response.json().get('status'):
            rjson = response.json()
            customer_data = rjson.get('data')
            self.first_name = customer_data.get('first_name')
            self.last_name = customer_data.get('last_name')
            self.phone = customer_data.get('phone')
            self.integration = customer_data.get('integration')
            self.code = customer_data.get('customer_code')
            self.id = customer_data.get('id')
            self.created_at = customer_data.get('createdAt')
            self.updated_at = customer_data.get('updatedAt')
            self.metadata = customer_data.get('metadata')
            self.email = customer_data.get('email')
            return "Customer Updated"


    @classmethod
    def fetch(cls, per_page=None, page=None):
        customers = []
        ps = Paystack()
        r = ps.requests
        params = {
            "perPage": per_page, 
            "page":page
        }
        params = {k:v for k,v in params.items() if bool(v)}
        response = r.get("{0}/customer".format(ps.root_url), params=params)
        if response.status_code == 200 and response.json().get('status'):
            rjson = response.json()
            customers_data = rjson.get('data')
            for c in customers_data:
                customers.append(cls.__from_json(c))
        return customers


    @classmethod
    def get(cls, identifier):
        ps = Paystack()
        r = ps.requests
        response = r.get("{0}/customer/{1}".format(ps.root_url,identifier))
        if response.status_code == 200 and response.json().get('status'):
            rjson = response.json()
            customer_data = rjson.get('data')
            customer = cls.__from_json(customer_data)
            return customer
        else:
            return None


    @staticmethod
    def __from_json(jdict):
        id = jdict.get('id')
        first_name = jdict.get('first_name')
        last_name = jdict.get('last_name')
        email = jdict.get('email')
        phone = jdict.get('phone')
        metadata = jdict.get('metadata')
        code = jdict.get('customer_code')
        created_at = jdict.get('createdAt')
        updated_at = jdict.get('updatedAt')
        integration = jdict.get('integration')
        c = Customer(email, first_name, last_name, phone)
        c.metadata = metadata
        c.id = id
        c.code = code
        c.created_at = created_at
        c.updated_at = updated_at
        c.integration = integration
        return c


class TransferReceipient:
    pass


class Transfer:
    pass