# -*- coding: utf-8 -*-
if not settings.done:
  try:
    if request.env.server_name == 'dms.domain.com':
        settings.migrate = True
        settings.title = 'Document Management System'
        settings.subtitle = 'powered by web2py'
        settings.author = 'Gyuris Szabolcs'
        settings.author_email = 'szimszon@oregpreshaz.eu'
        settings.keywords = ''
        settings.description = ''
        settings.database_uri = 'sqlite://dms.sqlite'
        settings.security_key = 'sha512:fef5fff7-ab4s-43e4-7eea-2fdd4515a4d2'
        settings.email_sender = 'root@localhost'
        settings.email_server = 'localhost'
        settings.env = 'production'
        settings.loglevel = logging.DEBUG
        settings.done = True
  except:
    pass
