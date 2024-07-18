import pyotp


def get_2fa_code(otp_code: str):
    totp = pyotp.TOTP(otp_code.replace(' ', ''))
    code = totp.now()
    return code