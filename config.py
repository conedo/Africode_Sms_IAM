
SECRET_KEY = 'QNpVVW590z6RWekgYZC9CIpNLHEqSwejZhl6JBx4Qv4'
SECURITY_PASSWORD_SALT = '30564915274344120077904866527843274912'
# database configuration
SQLALCHEMY_DATABASE_URI = "postgresql://dolly:40053@localhost:5432/sms"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINES_OPTIONS = {"pool_pre_ping": True,} 


# registration configuration
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = True

# cookie settings
REMEMBER_COOKIE_SAMESITE = 'strict'
SESSION_COOKIE_SAMESITE = 'strict'

# mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'chepkorirdolly4@gmail.com'
MAIL_PASSWORD = 'eswp xffn wmvk jkoz'
MAIL_DEFAULT_USER = 'dollychepkorir@gmail.com'

# Email settings
SECURITY_CHANGE_EMAIL = True

# recover/reset password
SECURITY_RECOVERABLE = True