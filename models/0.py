from gluon.storage import Storage

import logging
logger = logging.getLogger("web2py.app.dms")

settings = Storage()

settings.migrate = True
settings.title = 'Document Management System'
settings.subtitle = 'powered by web2py'
settings.author = 'Gyuris Szabolcs'
settings.author_email = 'szimszon@oregpreshaz.eu'
settings.keywords = ''
settings.description = ''
settings.database_uri = 'sqlite://dms.sqlite'
settings.security_key = 'sha512:fef5f707-a7e4-43e4-9eba-2675e515a4d2'
settings.email_sender = 'root@localhost'
settings.email_server = 'localhost'
settings.env = 'development'
settings.done = False
settings.loglevel = logging.DEBUG
