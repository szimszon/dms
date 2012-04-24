# -*- coding: utf-8 -*- 

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = T( 'DMS' )
response.subtitle = T( 'SOHO Document Management System' )

##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
		[T( 'Index' ), False,
		 URL( request.application, 'default', 'index' ), []],
		[T( 'Scan' ), False,
		 URL( request.application, 'default', 'scanner' ), []],
		[T( 'Store Scanned' ), False,
		 URL( request.application, 'default', 'store', vars = dict( source = 'scanner' ) ), []],
		[T( 'Store File' ), False,
		 URL( request.application, 'default', 'store', vars = dict( source = 'file' ) ), []],
		[T( 'Search Document' ), False,
		 URL( request.application, 'default', 'search' ), []],
		[T( 'Document form templates' ), False,
		 URL( request.application, 'default', 'templates' ), []],
		[T( 'Default actions' ), False,
		 URL( request.application, 'default', 'action/0' ), []],
		]


##########################################
## this is here to provide shortcuts
## during development. remove in production 
##########################################

response.menu_edit = [
  [T( 'Config' ), False,
    URL( request.application, 'jogok', 'config' ), []],
  [T( 'Check rights' ), False,
    URL( request.application, 'jogok', 'jogellenorzes' ), []],
  [T( 'Users' ), False,
    URL( request.application, 'jogok', 'users' ), []],
  [T( 'Add user to group' ), False,
    URL( request.application, 'jogok', 'addusertogroup' ), []],
	[T( 'Order tags' ), False,
		URL( request.application, 'jogok', 'ordertags' ), []],
  ]
