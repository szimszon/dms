#owldb = DAL( '...' )
#owldb.define_table( 'files',
#									 Field( 'name', 'string' ),
#									 Field( 'filename', 'string' ),
#									 Field( 'created', 'datetime' ),
#									 Field( 'description', 'text' ),
#									 Field( 'metadata', 'string' ),
#									 migrate = False )
#
#owldb.define_table( 'docfields',
#									 Field( 'doc_type_id', 'integer' ),
#									 Field( 'field_name', 'string' ),
#									 migrate = False )
#
#owldb.define_table( 'docfieldslabel',
#									 Field( 'doc_field_id', 'integer' ),
#									 Field( 'field_label', 'string' ),
#									 Field( 'locale', 'string' ),
#									 migrate = False )
#
#owldb.define_table( 'docfieldvalues',
#									 Field( 'field_name', 'string' ),
#									 Field( 'field_value', 'string' ),
#									 Field( 'file_id', owldb.files ),
#									 migrate = False )
