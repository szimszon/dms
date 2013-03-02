@auth.requires_login()
def index():
	dlist = owldb( ( owldb.files.id > 0 ) & \
							( owldb.files.id == owldb.docfieldvalues.file_id ) & \
							( ( owldb.docfields.field_name == owldb.docfieldvalues.field_name ) & \
							( owldb.docfieldslabel.doc_field_id == owldb.docfields.id ) ) & \
							( owldb.docfieldslabel.locale == 'English' )
							).select( owldb.files.id, owldb.files.name, owldb.files.filename, owldb.files.metadata,
											owldb.files.description, owldb.docfieldvalues.field_name, owldb.docfieldslabel.field_label,
											owldb.docfieldvalues.field_value )
	import os
	files = []
	for root, dirs, name in os.walk( '/srv/www/owl/Documents' ):
		for n in name:
			files.append( [root, n] )
	drows = {}
	for r in dlist:
		try:
			if not drows[r.files.id]['description'].count( "%s: %s\n" % ( r.docfieldslabel.field_label, r.docfieldvalues.field_value ) ):
				drows[r.files.id]['description'].append( "%s: %s\n" % ( r.docfieldslabel.field_label, r.docfieldvalues.field_value ) )
		except:
			drows[r.files.id] = dict( 
							title = r.files.name,
							body = r.files.description,
							description = ["%s: %s\n" % ( r.docfieldslabel.field_label, r.docfieldvalues.field_value )],
							tag = r.files.metadata.split(),
							file = [os.path.join( j[0], j[1] ) for j in files if j[1].count( r.files.filename ) ] )
			drows[r.files.id]['tag'].sort()
			drows[r.files.id]['tag'] = ','.join( drows[r.files.id]['tag'] )
	for dkey in drows:
		drows[dkey]['description'] = ''.join( drows[dkey]['description'] )
		#try:
		db.documents.insert( title = drows[dkey]['title'],
												tag = drows[dkey]['tag'],
												body = drows[dkey]['body'],
												comments = drows[dkey]['description'],
												file = db.documents.file.store( open( drows[dkey]['file'][0] ) ) )
		except:
			db.documents.insert( title = drows[dkey]['title'],
												tag = drows[dkey]['tag'],
												body = drows[dkey]['body'],
												comments = drows[dkey]['description'],
												 )
		formtags = drows[dkey]['tag'].replace( ', ', ',' ).lower().split( ',' )
		dbtags = [d.tag for d in db( db.tags.id > 0 ).select( db.tags.tag )]
		formtags = [u for u in formtags if dbtags.count( u ) == 0]
		for tag in formtags:
				db.tags.insert( tag = tag )

	return dict( drows = drows )
