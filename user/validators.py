import re

# 인자값으로 들어온 문자열이 password_regex에 정의된 조건들을 모두 만족하는지 검사합니다.
def password_validator(password):
    password_regex = '^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*()])[\w\d!@#$%^&*()]{8,}$'
    
    if not re.search(password_regex, str(password)):
        return True
    return False

# 인자값으로 들어온 문자열의 문자중 연속해서 3개 이상의 문자가 같은 패턴인지 검사합니다.
def password_pattern(password):
    password_pattern = r"(.)\1+\1"
    
    if re.search(password_pattern, str(password)):
        return True
    return False


def account_validator(account):
    account_validations = r"^[A-Za-z0-9]{5,20}$"
    
    if not re.search(account_validations, str(account)):
        return True
    return False


def nickname_validator(nickname):
    nickname_validation = r"^[A-Za-z가-힣0-9]{2,8}$"
    
    if not re.search(nickname_validation, str(nickname)):
        return True
    return False