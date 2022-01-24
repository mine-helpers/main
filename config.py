import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or '%q@vzm)&ag&ftcv+9a8tb55-hw@6*4dez#$%$1rxq57ddv@&9s'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kfpdashboard@gmail.com'
    MAIL_PASSWORD = 'aQUto&o876*!dtXyN4333!'
    KEFA_MAIL_SUBJECT_PREFIX = '[KEFA]'
    KEFA_MAIL_SENDER = 'KEFA Admin <kfpdashboard@gmail.com>'
    KEFA_ADMIN = os.environ.get('KEFA_ADMIN') or 'kfpdashboard@gmail.com'
    KEFA_POSTS_PER_PAGE = 100
    KEFA_FOLLOWERS_PER_PAGE = 50
    KEFA_COMMENTS_PER_PAGE = 30
    KEFA_SLOW_DB_QUERY_TIME = 0.5
    CLICKATELL_API_KEY = 'dhweu3e82edusdsdhweayduwkewe'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SSL_DISABLE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://postgres:aQUto&o876*!@localhost/kfpdb'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SSL_DISABLE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localadmin:aQUto&o876*!@localhost/kfpdb'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.KEFA_MAIL_SENDER,
            toaddrs=[cls.KEFA_ADMIN],
            subject=cls.KEFA_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}
