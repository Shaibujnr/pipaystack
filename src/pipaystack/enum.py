import enum


class TransactionStatus(enum.Enum):
    SUCCESS = 1
    FAILED = 2
    ABANDONED = 3
    SEND_PIN = 4
    SEND_OTP = 5
    SEND_PHONE = 6
    SEND_BIRTHDAY = 7
    OPEN_URL = 8
    PENDING = 9
    ONGOING = 10


    @classmethod
    def from_string(cls, status_string):
        status_string_mapping = {
            'success': cls.SUCCESS,
            'failed': cls.FAILED,
            'abandoned': cls.ABANDONED,
            'send_pin': cls.SEND_PIN,
            'send_otp': cls.SEND_OTP,
            'send_phone': cls.SEND_PHONE,
            'send_birthday': cls.SEND_BIRTHDAY,
            'open_url': cls.OPEN_URL,
            'pending': cls.PENDING,
            'ongoing': cls.ONGOING
        }
        return status_string_mapping[status_string]

    
    def __str__(self):
        if self == self.SUCCESS:
            return 'success'
        if self == self.FAILED:
            return 'failed'
        if self == self.ABANDONED:
            return 'abandoned'
        if self == self.ONGOING:
            return 'ongoing'


class ChargeType(enum.Enum):
    CARD = 1
    BANK = 2


class Bank(enum.Enum):
    ACCESS = '044'
    ALAT_BY_WEMA = '035A'
    ASO_SAVINGS_AND_LOANS = '401'
    CITI = '023'
    DIAMOND = '063'
    ECOBANK = '050'
    EKONDO_MICROFINANCE_BANK = '562'
    ENTERPRISE = '084'
    FIDELITY = '070'
    FIRST = '011'
    FCMB = '214'
    GTB = '058'
    HERITAGE = '030'
    JAIZ = '301'
    KEYSTONE = '082'
    MAINSTREET = '014'
    PARALLEX = '526'
    POLARIS = '076'
    PROVIDUS = '101'
    STANBIC_IBTC = '221'
    STANDARD_CHARTERED = '068'
    STERLING = '232'
    SUNTRUST = '100'
    UNION = '032'
    UBA = '033'
    UNITY = '215'
    WEMA = '035'
    ZENITH = '057'
