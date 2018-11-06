import pytest
from pipaystack.models import Paystack


@pytest.fixture(scope='function')
def ps():
    f = open('cred.txt', 'r')
    secret = f.read()
    return Paystack(secret=secret)