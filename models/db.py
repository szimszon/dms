# -*- coding: utf-8 -*- 

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:						# if running on Google App Engine
		db = DAL('gae')													 # connect to Google BigTable
		session.connect(request, response, db=db) # and store sessions and tickets there
		### or use the following lines to store sessions in Memcache
		# from gluon.contrib.memdb import MEMDB
		# from google.appengine.api.memcache import Client
		# session.connect(request, response, db = MEMDB(Client()))
else:																				 # else use a normal relational database
		if request.env.server_name == 'gimli':
				db = DAL('sqlite://dms.sqlite')			 # if not, use SQLite or other DB
		else:
				db = DAL('mysql://dms:YRecki347@localhost/dms')
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for 
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################
session.connect(request, response, db, masterapp=None)
from gluon.tools import *
mail = Mail()																	# mailer
auth = Auth(globals(), db)											# authentication/authorization
crud = Crud(globals(), db)											# for CRUD helpers using auth
service = Service(globals())									 # for json, xml, jsonrpc, xmlrpc, amfrpc

#mail.settings.server = 'logging' or 'smtp.gmail.com:587'	# your SMTP server
#mail.settings.sender = 'you@gmail.com'				 # your email
#mail.settings.login = 'username:password'			# your credentials or None
mail.settings.server = 'localhost'
mail.settings.sender = 'szimszon@oregpreshaz.eu'


auth.settings.hmac_key = 'sha512:fef5f707-a7e4-43e4-9eba-2675e515a4d2'	 # before define_tables()
auth.define_tables()													 # creates all needed tables
auth.settings.mailer = mail										# for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://' + request.env.http_host + URL(r=request, c='default', f='user', args=['verify_email']) + '/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://' + request.env.http_host + URL(r=request, c='default', f='user', args=['reset_password']) + '/%(key)s to reset your password'

crud.settings.auth = auth											# =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##			 'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
db.define_table('tags',
								Field('tag', 'string',
											label=T('Tag'),
											requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'tags.tag')]))

db.define_table('templates',
								Field('name', 'string',
											label=T('Name'),
											requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'templates.name')],
											),
								Field('dgroup', 'string',
											label=T('Document group'),
											),
								Field('title', 'string',
											label=T('Title'),
											),
								Field('tag', 'string',
											label=T('Tags'),
											requires=IS_NOT_EMPTY(),
											),
								Field('body', 'text',
											label=T('Body')
											),
								Field('comments', 'text',
											label=T('Comments')
											),
								Field('expire_on', 'string',
											label=T('Expiration date'),
											),
								Field('active', 'boolean',
											label=T('Active'),
											default=True,
											),
								Field('created_by', db.auth_user,
											label=T('Created by'),
											default=auth.user_id,
											writable=False,
											),
								Field('created_on', 'datetime',
											label=T('Created on'),
											requires=IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S')),
											default=request.now,
											writable=False,
											),
								Field('modified_by', db.auth_user,
											label=T('Last modified by'),
											default=auth.user_id,
											update=auth.user_id,
											writable=False,
											),
								Field('modified_on', 'datetime',
											label=T('Last modified on'),
											requires=IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S')),
											default=request.now,
											update=request.now,
											writable=False,
											)
								)

db.define_table('documents',
								Field('title', 'string',
											label=T('Title'),
											requires=IS_NOT_EMPTY(),
											),
								Field('tag', 'string',
											label=T('Tags'),
											requires=IS_NOT_EMPTY(),
											),
								Field('file', 'upload',
											label=T('File'),
											uploadseparate=True,
											),
								Field('body', 'text',
											label=T('Body')
											),
								Field('comments', 'text',
											label=T('Comments')
											),
								Field('expire_on', 'date',
											label=T('Expiration date'),
											requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d'))),
											),
								Field('created_by', db.auth_user,
											label=T('Created by'),
											default=auth.user_id,
											writable=False,
											),
								Field('created_on', 'datetime',
											label=T('Created on'),
											requires=IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S')),
											default=request.now,
											writable=False,
											),
								Field('modified_by', db.auth_user,
											label=T('Last modified by'),
											default=auth.user_id,
											update=auth.user_id,
											writable=False,
											),
								Field('modified_on', 'datetime',
											label=T('Last modified on'),
											requires=IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S')),
											default=request.now,
											update=request.now,
											writable=False,
											),
								)

db.define_table('action',
							Field('documents_id', 'integer',
									label=T('Documents ID'),
									writable=False,
									),
							Field('name', 'string',
									label=T('Action name'),
									requires=IS_NOT_EMPTY()),
							Field('atype', 'string',
									label=T('Action type'),
									requires=IS_IN_SET(['new', 'modified', 'expired', 'other'],
																			[T('New'), T('Modified'), T('Expired'), T('Other')],
																			 zero=None)),
							Field('email', 'string',
									label=T('E-mail'),
									requires=IS_EMAIL(),),
							Field('adate', 'date',
									label=T('Date to do'),
									requires=IS_NULL_OR(IS_DATE(T('%Y-%m-%d')))),
							Field('mbody', 'text',
									label=T('Message body'),
									default=T("""Automated message from DMS

Action name: $actname
Action type: $acttype
Action date: $actdate

Document    : $docname
Document url: $docurl
File url    : $fileurl

""")
									),
							Field('done', 'boolean',
									label=T('Done'),
									default=False),
							Field('created_by', db.auth_user,
										label=T('Created by'),
										default=auth.user_id,
										writable=False,
										),
							Field('created_on', 'datetime',
										label=T('Created on'),
										requires=IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S')),
										default=request.now,
										writable=False,
										),
							Field('modified_by', db.auth_user,
										label=T('Last modified by'),
										default=auth.user_id,
										update=auth.user_id,
										writable=False,
										),
							Field('modified_on', 'datetime',
										label=T('Last modified on'),
										requires=IS_DATETIME(format=T('%Y-%m-%d %H:%M:%S')),
										default=request.now,
										update=request.now,
										writable=False,
										),
							)

db.define_table('papersize',
							Field('name', 'string',
									label="Papersize",
									requires=IS_LOWER()),
							Field('x', 'integer',
									label="Width (mm)",
									requires=IS_NOT_EMPTY()),
							Field('y', 'integer',
									label="Hight (mm)",
									requires=IS_NOT_EMPTY())
							)

db.define_table('scannerconfig',
								Field('device', 'string',
											label=T('Scanner'),
											requires=IS_IN_SET(['None', 'None']),),
								Field('size', db.papersize,
											label=T('Papersize'),
											requires=IS_NULL_OR(
																	IS_IN_DB(db,
																					db.papersize.id,
																					'%(name)s (%(x)smm X %(y)smm)',
																					zero=T('Default')))
											),
								Field('resolution', 'integer',
											label=T('Resolution'),
											requires=IS_IN_SET(['150', '200']),
											),
								Field('mode', 'string',
											label=T('Mode'),
											requires=IS_NULL_OR(
																		IS_IN_SET(['Lineart', 'Gray' , 'Color' ],
																							[T('Lineart'), T('Gray'), T('Color')] ,
																					 zero=T('Default'))),
											),
								Field('moreparams', 'string',
											label=T('More scanimage params'),
											comment=T('command line arguments')),
								Field('lang', 'string',
											label=T('Language'),
											requires=IS_IN_SET(['hun', 'eng', 'ger']),),
								Field('auth_user_id', db.auth_user,
											label=T('User'),
											requires=IS_IN_DB(db, 'auth_user.id', '%(last_name)s %(first_name)'),
											readable=False,
											writable=False,
											),

								)
db.define_table('config',
								Field('resolution', 'string',
											label=T('Scanner resolution'),
											requires=IS_NOT_EMPTY(),
											default='50,100,150,200,250,300,400,500,600,1200' ,
											comment=T('comma separated list of numbers')),
								Field('prgscanimage', 'string',
											label=T('"scanimage" binary'),
											requires=IS_NOT_EMPTY(),
											default='/usr/bin/scanimage'),
								Field('prgconvert', 'string',
											label=T('"convert" binary'),
											requires=IS_NOT_EMPTY(),
											default='/usr/bin/convert'),
								Field('ocr', 'string',
											label=T('ocr commandline'),
											default='/usr/local/bin/tesseract $filefrom $fileto -lang $lang' ,
											comment=T('subs.: $filefrom - the file to recognize, $fileto - the text file, $lang - how to put the selected language')),
								Field('fileext', 'string',
											label=T('File extension'),
											default='txt',
											comment=T('tesseract puts .txt after $fileto')),
								Field('urlbase', 'string',
											label=T('URL base'),
											requires=IS_NOT_EMPTY(),
											default='https://domain.tld	'),
								)


exec("import applications.%s.modules.wszelper as wszelper" % \
			 request.application)
reload(wszelper)

seged = wszelper.WSzelper(globals(), db)
