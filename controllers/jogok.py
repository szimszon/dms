@auth.requires_login()
@auth.requires_membership( 'user_1' )
def jogellenorzes():
		text = "dms csoport ellenőrzése... "
		query = ( db.auth_group.role == 'dms' )
		if ( int( db( query ).count() ) == 0 ):
					def_group_id = auth.add_group( 'dms', 'Document Management csoport' )
					text += "létrehozva.<br />"
		else:
				def_group_id = db( query ).select( db.auth_group.id )[0].id
				text += "OK.<br />"
		# ures szemely
		for group_id in [def_group_id]:
			text += "<center>GroupID: " + str( group_id ) + "</center><br />"
			for tbl in ['scannerconfig', 'documents', 'templates', 'action']:
				text += "<center>Table: " + tbl + "</center><br />"
				for role in ['create', 'read', 'update', 'delete', 'select']:
					text += tbl + " tábla " + role + " jog ellenőrzése... "
					pquery = ( ( db.auth_permission.group_id == group_id ) &
												( db.auth_permission.name == role ) &
												( db.auth_permission.table_name == tbl ) )
					if ( db( pquery ).count() > 0 ):
						text += " OK.<br />"
					else:
						auth.add_permission( group_id, role, tbl, 0 )
						text += " létrehozva.<br />"
		def_group_id = db( db.auth_group.role == 'user_1' ).select( db.auth_group.id )[0].id
		for group_id in [def_group_id]:
			text += "<center>GroupID: " + str( group_id ) + "</center><br />"
			for tbl in ['config', 'auth_membership', 'auth_user']:
				text += "<center>Table: " + tbl + "</center><br />"
				for role in ['create', 'read', 'update', 'delete', 'select']:
					text += tbl + " tábla " + role + " jog ellenőrzése... "
					pquery = ( ( db.auth_permission.group_id == group_id ) &
												( db.auth_permission.name == role ) &
												( db.auth_permission.table_name == tbl ) )
					if ( db( pquery ).count() > 0 ):
						text += " OK.<br />"
					else:
						auth.add_permission( group_id, role, tbl, 0 )
						text += " létrehozva.<br />"



		papersize = {}
		papersize['a0'] = dict( x = 841, y = 1189 )
		papersize['a1'] = dict( x = 594, y = 841 )
		papersize['a2'] = dict( x = 420, y = 594 )
		papersize['a3'] = dict( x = 297, y = 420 )
		papersize['a4'] = dict( x = 210, y = 297 )
		papersize['a5'] = dict( x = 148, y = 210 )
		papersize['a6'] = dict( x = 105, y = 148 )
		papersize['a7'] = dict( x = 74, y = 105 )
		papersize['a8'] = dict( x = 52, y = 74 )
		papersize['a9'] = dict( x = 37, y = 52 )
		papersize['a10'] = dict( x = 26, y = 37 )
		papersize['b0'] = dict( x = 1000, y = 1414 )
		papersize['b1'] = dict( x = 707, y = 1000 )
		papersize['b2'] = dict( x = 500, y = 707 )
		papersize['b3'] = dict( x = 353, y = 500 )
		papersize['b4'] = dict( x = 250, y = 353 )
		papersize['b5'] = dict( x = 176, y = 250 )
		papersize['b6'] = dict( x = 125, y = 176 )
		papersize['b7'] = dict( x = 88, y = 125 )
		papersize['b8'] = dict( x = 62, y = 88 )
		papersize['b9'] = dict( x = 44, y = 62 )
		papersize['b10'] = dict( x = 31, y = 44 )
		papersize['c0'] = dict( x = 917, y = 1297 )
		papersize['c1'] = dict( x = 648, y = 917 )
		papersize['c2'] = dict( x = 458, y = 648 )
		papersize['c3'] = dict( x = 324, y = 458 )
		papersize['c4'] = dict( x = 229, y = 324 )
		papersize['c5'] = dict( x = 162, y = 229 )
		papersize['c6'] = dict( x = 114, y = 162 )
		papersize['c7'] = dict( x = 81, y = 114 )
		papersize['c8'] = dict( x = 57, y = 81 )
		papersize['c9'] = dict( x = 40, y = 57 )
		papersize['c10'] = dict( x = 28, y = 40 )
		papersize['letter'] = dict( x = 216, y = 279 )
		papersize['legal'] = dict( x = 216, y = 356 )
		for ps in papersize.keys():
			if db( db.papersize.name == ps ).count() == 0:
				text += "Papersize %s added...<br/>" % ps
				db.papersize.insert( name = ps,
													x = papersize[ps]['x'],
													y = papersize[ps]['y'], )
			else:
				text += "Papersize %s OK.<br/>" % ps
		return dict( text = XML( text ) )

@auth.requires_login()
@auth.requires_membership( 'user_1' )
def users():
    form = crud.update( db.auth_user, request.args( 1 ) )
    userlist = db( db.auth_user.id > 0 ).select( db.auth_user.id,
                                          db.auth_user.first_name,
                                          db.auth_user.last_name,
                                          db.auth_user.email, )
    return dict( form = form, userlist = SQLTABLE( userlist,
                                            linkto = URL( r = request ),
                                            orderby = True ) )

@auth.requires_login()
@auth.requires_membership( 'user_1' )
def addusertogroup():
    form = crud.update( db.auth_membership, request.args( 1 ) )
    userlist = db( db.auth_membership.id > 0 ).select()
    return dict( form = form, userlist = SQLTABLE( userlist,
                                            linkto = URL( r = request ),
                                            orderby = True ) )

@auth.requires_login()
@auth.requires_membership( 'user_1' )
def config():
	try:
		cid = db( db.config.id > 0 ).select( limitby = ( 0, 1 ) )[0].id
	except:
		cid = None
	form = crud.update( db.config, cid )
	return dict( form = form )

@auth.requires_login()
@auth.requires_membership( 'user_1' )
def ordertags():
	recs = db( db.documents.id > 0 ).select( db.documents.id, db.documents.tag )
	msg = ''
	for r in recs:
		formtags = r.tag.replace( ', ', ',' ).lower().split( ',' )
		formtags.sort()
		formtags = ','.join( formtags )
		if db( db.documents.id == r.id ).update( tag = formtags ):
			msg += "%s -> [%s] ok<br/>" % ( r.id, formtags )
		else:
			msg += "%s -> [%s] err<br/>" % ( r.id, formtags )
	return dict( msg = XML( msg ) )

