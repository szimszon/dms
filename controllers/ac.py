@auth.requires_login()
def index():
    return dict()

@auth.requires_login()
def templates():
		def repleace( txt ):
				import re
				import datetime
				if not txt:
						return None
				txt = str( txt )
				re_subplus = re.compile( "\{\$(?P<var>\w+)(?P<number>[+-]\d+)\}" )
				m = re_subplus.search( txt )
				while ( m ):
						v = m.group( 'var' )
						n = m.group( 'number' )
						if ( v == 'date' ):
								rtxt = ( request.now.date() + datetime.timedelta( days = int( n ) ) ).strftime( str( T( '%Y-%m-%d' ) ) )
						elif ( v == 'time' ):
								rtxt = str( request.now.time() + datetime.timedelta( seconds = int( n ) * 60 ) )
						elif ( v == 'YYYY' ):
								rtxt = str( int( request.now.year ) + int( n ) )
						elif ( v == 'mm' ):
								month = ( int( request.now.month ) + int( n ) ) % 12
								rtxt = '%02d' % ( month )
						elif ( v == 'dd' ):
								day = ( int( request.now.day ) + int( n ) ) % 31
								rtxt = '%02d' % ( day )
						elif ( v == 'HH' ):
								hour = ( int( request.now.hour ) + int( n ) ) % 24
								rtxt = '%02d' % ( hour )
						elif ( v == 'MM' ):
								minute = ( int( request.now.minute ) + int( n ) ) % 59
								rtxt = '%02d' % ( minute )
						elif ( v == 'SS' ):
								second = ( int( request.now.second ) + int( n ) ) % 59
								rtxt = '%02d' % ( seconds )
						try:
								txt = re_subplus.sub( rtxt, txt, count = 1 )
						except:
								txt = re_subplus.sub( '#ERR:[%s]' % str( v ), txt, count = 1 )
						m = re_subplus.search( txt )
				re_subplus = re.compile( "\{\$(?P<var>\w+)\}" )
				m = re_subplus.search( txt )
				while ( m ):
						v = m.group( 'var' )
						if ( v == 'date' ):
								rtxt = ( request.now.date() ).strftime( str( T( '%Y-%m-%d' ) ) )
						elif ( v == 'time' ):
								rtxt = str( request.now.time() )
						elif ( v == 'YYYY' ):
								rtxt = str( request.now.year )
						elif ( v == 'mm' ):
								rtxt = '%02d' % int( request.now.month )
						elif ( v == 'dd' ):
								rtxt = '%02d' % int( request.now.day )
						elif ( v == 'HH' ):
								rtxt = '%02d' % int( request.now.hour )
						elif ( v == 'MM' ):
								rtxt = '%02d' % int( request.now.minute )
						elif ( v == 'SS' ):
								rtxt = '%02d' % int( request.now.second )
						elif ( v == 'user' ):
								rtxt = str( T( '%(first_name)s %(last_name)s', dict( first_name = auth.user.first_name,
																													 last_name = auth.user.last_name ) ) )
						try:
								txt = re_subplus.sub( rtxt, txt, count = 1 )
						except:
								txt = re_subplus.sub( '#ERR:[%s]' % str( v ), txt, count = 1 )
						m = re_subplus.search( txt )
				m = None
				return txt

		if not request.args:
				return '#ERR - no args'
		r = dict( title = '',
					 tag = '',
					 comments = '',
					 body = '',
					 expire_on = '' )
		try:
				record = db( db.templates.active == True )( db.templates.id == request.args[0] ).select( limitby = ( 0, 1 ) )[0]
		except:
				return r
		r = dict( title = repleace( record.title ),
				 tag = repleace( record.tag ),
				 comments = repleace( record.comments ),
				 body = repleace( record.body ),
				 expire_on = repleace( record.expire_on ),
				 )
		return r

@auth.requires_login()
def tags():
		'''
			tagek kigyujtese, autocomplet
		'''
		import re
		re_x = re.compile( '^(?P<eleje>.*),[ ]*(?P<vege>[^,]*)$' )
		q = ""
		if request.vars:
				q = request.vars.q
		if not q:
				return q
		m = re_x.match( q )
		if not m:
			vege = q
			eleje = ''
		else:
			vege = m.group( 'vege' )
			eleje = m.group( 'eleje' )
		# kikeressuk a sorokat, amik hasonlitanak a beirt kifejezeshez
		rows = db( db.tags.tag.like( '%' + vege.decode( 'utf-8' ).lower() + '%' ) ).select()

		# kiszedjuk soronkent
		r = ""
		qa = q.replace( ', ', ',' ).lower().split( ',' )
		for row in rows:
				s = str( row.tag ).lower()
				if ( qa.count( s ) == 0 ):
						if eleje == '':
							r += "\n%s" % ( s )
						else:
							r += "\n%s,%s" % ( eleje, s )
		return r

@auth.requires_login()
def title():
		'''
			title kigyujtese, autocomplet
		'''
		q = ""
		if request.vars:
				q = request.vars.q
		if not q:
				return q
		# kikeressuk a sorokat, amik hasonlitanak a beirt kifejezeshez
		rows = db( db.documents.title.lower().like( '%' + q.decode( 'utf-8' ).lower() + '%' ) ).select()

		# kiszedjuk soronkent
		r = ""
		for row in rows:
				r += "\n%s" % ( row.title )
		return r
