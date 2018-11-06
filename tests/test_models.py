import pytest
import time
from pipaystack.models import Paystack, Transaction, TransactionStatus


@pytest.mark.first
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


def test_initialize_transaction_with_reference(ps):
    ref = str(int(round(time.time() * 1000)))
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

