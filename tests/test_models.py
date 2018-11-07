import pytest
from pipaystack.models import Paystack, Transaction, Customer
from pipaystack.enum import TransactionStatus, ChargeType, Bank


@pytest.mark.tryfirst
def test_paystack_singleton_not_initialized():
    with pytest.raises(Exception):
        p1 = Paystack()


def test_paystack_singleton():
    p1 = Paystack("secret_key")
    p2 = Paystack()
    assert p1 == p2
    assert p2.secret == "secret_key"
    assert p1.requests.headers.get("Authorization") == p2.requests.headers.get("Authorization")
    p3 = Paystack("new_secret")
    assert p1 == p2 == p3
    assert p1.secret == p2.secret == "new_secret"
    assert p1.requests.headers.get("Content-Type") == "application/json"
    assert "Authorization" in p1.requests.headers
    assert (
         p1.requests.headers.get("Authorization") ==
         p2.requests.headers.get("Authorization") ==
         p3.requests.headers.get("Authorization") )


def test_initialize_transaction(ps):
    t = Transaction.initialize(
        email = "test_initialize@gmail.com",
        amount = 25400
    )
    print(t.authorization_url)
    assert t is not None
    assert t.reference is not None
    assert t.metadata is None
    assert t.authorization_url is not None


def test_initialize_transaction_with_reference(ps, ref):
    t = Transaction.initialize(
        email = "test_initialize_with_reference@gmail.com",
        amount = 4500,
        reference = ref
    )
    print(t.authorization_url)
    assert t is not None
    assert t.reference == ref
    assert t.authorization_url is not None


def test_fetch_transactions(ps):
    ts = Transaction.fetch()
    assert isinstance(ts, list)
    assert len(ts) > 0
    assert isinstance(ts[0], Transaction)

def test_fetch_transactions_with_filter(ps):
    ts = Transaction.fetch(per_page=3)
    assert len(ts) == 3
    ts = Transaction.fetch(per_page=5, status=str(TransactionStatus.SUCCESS))
    for t in ts:
        assert t.status == TransactionStatus.SUCCESS


def test_get_transaction(ps):
    tts = Transaction.fetch()[0]
    ts = Transaction.get(tts.id)
    assert ts.id == tts.id
    assert ts.reference == tts.reference
    assert ts.ip == tts.ip
    assert ts.paid_at == tts.paid_at
    assert ts.created_at == tts.created_at


def test_verify_transaction(ps):
    ts = Transaction.fetch(per_page=1, status=TransactionStatus.SUCCESS)
    tt = ts[0]
    t = Transaction(tt.reference)
    assert t.id is None
    assert t.status is None
    assert t.reference == tt.reference
    status = t.verify()
    assert status == TransactionStatus.SUCCESS
    assert t.id is not None
    assert t.status == TransactionStatus.SUCCESS
    assert t.id == tt.id


def test_charge_start_method(ps):
    from inspect import signature
    email = "s.shaibu.jnr@gmail.com"
    amount = 30000
    card_charge = Transaction.charge(ChargeType.CARD, email, amount)
    assert callable(card_charge.start)
    sig = signature(card_charge.start)
    assert len(sig.parameters) == 6
    bank_charge = Transaction.charge(ChargeType.BANK, email, amount)
    assert callable(bank_charge.start)
    sig = signature(bank_charge.start)
    assert len(sig.parameters) == 5


def test_bank_charge_with_bank_enum(ps, ref):
    email = "test_bank_charge_with_bank_enum@gmail.com"
    amount = 450000
    bank = Bank.ZENITH
    account_number = "0000000000"
    birthday = "1995-12-23"
    otp = "123456"
    bank_charge = Transaction.charge(ChargeType.BANK, email, amount)
    ts = bank_charge.start(bank, account_number, reference=ref)
    assert isinstance(ts, Transaction)
    assert ts.reference == ref
    assert ts.status == TransactionStatus.SEND_BIRTHDAY
    ts.authorize_birthday(birthday)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SUCCESS

def test_bank_charge_with_bank_code(ps, ref):
    email = "test_bank_charge_with_bank_code@gmail.com"
    amount = 230980
    account_number = "0000000000"
    birthday = "1995-12-23"
    otp = "123456"
    bank_charge = Transaction.charge(ChargeType.BANK, email, amount)
    ts = bank_charge.start(None, account_number, reference=ref, bank_code='057')
    assert isinstance(ts, Transaction)
    assert ts.reference == ref
    assert ts.status == TransactionStatus.SEND_BIRTHDAY
    ts.authorize_birthday(birthday)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SUCCESS


def test_bank_charge_with_wrong_bank_enum_and_correct_code(ps, ref):
    email = "test_bank_charge_with_wrong_bank_enum_and_correct_code@gmail.com"
    amount = 15700
    bank = Bank.FCMB
    account_number = "0000000000"
    birthday = "1995-12-23"
    otp = "123456"
    bank_charge = Transaction.charge(ChargeType.BANK, email, amount)
    ts = bank_charge.start(bank, account_number, reference=ref, bank_code='057')
    assert isinstance(ts, Transaction)
    assert ts.reference == ref
    assert ts.status == TransactionStatus.SEND_BIRTHDAY
    ts.authorize_birthday(birthday)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SUCCESS


def test_bank_charge_with_correct_bank_enum_and_wrong_code(ps, ref):
    email = "test_bank_charge_with_correct_bank_enum_and_wrong_code@gmail.com"
    amount = 15700
    bank = Bank.ZENITH
    account_number = "0000000000"
    bank_charge = Transaction.charge(ChargeType.BANK, email, amount)
    ts = bank_charge.start(bank, account_number, reference=ref, bank_code=Bank.GTB.value)
    assert isinstance(ts, Transaction)
    assert ts.reference == ref
    assert ts.status == TransactionStatus.FAILED
    

def test_card_charge_with_no_validation(ps, future_year):
    email = "test_card_charge_with_no_validation@gmail.com"
    amount = 30000
    card_charge = Transaction.charge(ChargeType.CARD, email, amount)
    ts = card_charge.start('4084084084084081', '408', '01', future_year)
    assert isinstance(ts, Transaction)
    assert ts.status == TransactionStatus.SUCCESS


def test_card_charge_with_pin_and_otp_validation(ps, ref, future_year):
    email = 'test_card_charge_with_pin_and_otp_validation@gmail.com'
    amount = 18700
    pin = '1234'
    otp = '123456'
    card_charge = Transaction.charge(ChargeType.CARD, email, amount)
    ts = card_charge.start('5060666666666666666', '123', '02', future_year, reference=ref)
    assert isinstance(ts, Transaction)
    assert ts.status == TransactionStatus.SEND_PIN 
    ts.authorize_pin(pin)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SUCCESS


def test_card_with_pin_validation(ps, ref, future_year):
    email = 'test_card_charge_with_pin_validation@gmail.com'
    amount = 1900
    pin = '1111'
    card_charge = Transaction.charge(ChargeType.CARD, email, amount)
    ts = card_charge.start('507850785078507812', '081', '02', future_year, reference=ref)
    assert isinstance(ts, Transaction)
    assert ts.status == TransactionStatus.SEND_PIN 
    ts.authorize_pin(pin)
    assert ts.status == TransactionStatus.SUCCESS


def test_card_charge_with_pin_phone_otp_validation(ps, ref, future_year):
    email = 'test_card_charge_with_pin_phone_otp_validation@gmail.com'
    amount = 4570
    cn = "50785078507850784"
    cvv = '884'
    pin = '0000'
    phone = '12390876544'
    otp = '123456'
    card_charge = Transaction.charge(ChargeType.CARD, email, amount)
    ts = card_charge.start(cn, cvv, '02', future_year, reference=ref)
    assert isinstance(ts, Transaction)
    assert ts.status == TransactionStatus.SEND_PIN 
    ts.authorize_pin(pin)
    assert ts.status == TransactionStatus.SEND_PHONE
    ts.authorize_phone(phone)
    assert ts.status == TransactionStatus.SEND_OTP
    ts.authorize_otp(otp)
    assert ts.status == TransactionStatus.SUCCESS

def test_card_charge_with_incomeplete_validation(ps, ref, future_year):
    email = 'test_card_charge_with_incomplete_validation@gmail.com'
    amount = 4570
    cn = "50785078507850784"
    cvv = '884'
    pin = '0000'
    phone = '12390876544'
    otp = '123456'
    card_charge = Transaction.charge(ChargeType.CARD, email, amount)
    ts = card_charge.start(cn, cvv, '02', future_year, reference=ref)
    assert isinstance(ts, Transaction)
    assert ts.status == TransactionStatus.SEND_PIN 
    ts.authorize_pin(pin)
    assert ts.status == TransactionStatus.SEND_PHONE
    ts.authorize_phone(phone)


def test_customer_creation(ps):
    email = 'johndoe@gmail.com'
    if isinstance(Customer.get(email),Customer):
        pytest.skip("Customer already exists")
    c = Customer(email, "John", "Doe", "08012345678", from_test=True, hello='hi')
    assert c.id is None
    assert c.code is None
    c.create()
    assert c.id is not None
    assert c.code is not None
    assert c.metadata == {'from_test':True,'hello':'hi'}


def test_customer_fetch(ps):
    customers = Customer.fetch()
    assert isinstance(customers, list)
    assert len(customers) > 0
    assert isinstance(customers[0], Customer)


def test_customer_fetch_with_filter(ps):
    cs = Customer.fetch(per_page=2)
    assert isinstance(cs, list)
    assert len(cs) == 2
    assert isinstance(cs[0], Customer)
    cs1 = Customer.fetch(per_page=1, page=1)
    cs2 = Customer.fetch(per_page=1, page=2)
    assert cs1[0] is not None
    assert cs2[0] is not None
    assert cs1[0].id != cs2[0].id


def test_customer_get(ps):
    tc = Customer.fetch(per_page=1, page=4)[0]
    ec = Customer.get(tc.email)
    cc = Customer.get(tc.code)
    ic = Customer.get(tc.id)
    assert ec.id == cc.id == ic.id == tc.id
    assert ec.email == cc.email == ic.email == tc.email

def test_get_customer_with_wrong_id(ps):
    cc = Customer.get('NonethisIddoesnotexisteitherasemailorcodeorid')
    assert cc is None

def test_upddate_customer(ps):
    c = Customer.fetch(per_page=1, page=4)[0]
    msg = c.update(
        first_name="UpdateFirstName",last_name="UpdateLastName",phone="updatephone123",extra='from_test',typ='update'
    )
    assert msg == "Customer Updated"
    tc = Customer.get(c.id)
    assert tc.first_name == "UpdateFirstName"
    assert tc.last_name == "UpdateLastName"
    assert tc.phone == "updatephone123"
    assert tc.metadata == {'extra':'from_test', 'typ':'update'}


def test_fetch_customer_transactions(ps):
    c = Customer.get('s.shaibu.jnr@gmail.com')
    ct = c.transactions
    assert isinstance(ct, list)
    assert len(ct) > 0
    assert isinstance(ct[0], Transaction)


def test_setting_customer_transactions(ps):
    with pytest.raises(AttributeError):
        c = Customer.get('s.shaibu.jnr@gmail.com')
        c.transactions = [1,2,3]