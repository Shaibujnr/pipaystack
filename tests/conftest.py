import pytest
import time
import datetime
from pipaystack.models import Paystack


@pytest.fixture(scope='function')
def ps():
    f = open('cred.txt', 'r')
    secret = f.read()
    return Paystack(secret=secret)

@pytest.fixture
def ref():
    s = str(int(round(time.time() * 1000)))
    print('\n%s\n'%s)
    return s

@pytest.fixture
def future_year():
    return datetime.datetime.now().year+1