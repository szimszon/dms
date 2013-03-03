# -*- coding: utf-8 -*- 

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################    

def crondaily():
    if request.client != '127.0.0.1':
        return ''
    return str(doaction(None, 'cron'))

def doaction(form, atype):
    import string
    urlbase = db(db.config.id > 0).select(limitby=(0, 1)).first().urlbase
    if atype == 'cron':
        actionlist = db(((db.action.done != True) &
                                            ((db.documents.id == db.action.documents_id) &
                                                      ((db.action.adate == request.now) |
                                                                 (
                                                                    (db.documents.expire_on == request.now) &
                                                                    (db.action.atype == 'expired')
                                                                )
                                                        )
                                            )) | (
                                                        ((db.action.atype == 'expired') & (db.action.documents_id == 0) &
                                                        (db.documents.expire_on == request.now))
                                                    )
                                                      ).select()
    elif atype == 'other':
        actionlist = None
    elif atype == 'new' or atype == 'modified':
        actionlist = db(((db.action.done != True) &
                                             (db.action.documents_id == form.vars.id) &
                                             (db.action.atype == atype)
                                            )
                                             | (
                                                        ((db.action.atype == atype) & (db.action.documents_id == 0) &
                                                        (db.documents.id == form.vars.id))
                                                    )
                                                      ).select()

    err = ''
    mailbody = ''
    for act in actionlist:
        svars = dict(url=request.url,
                        actname=act.action.name,
                        acttype=T(str(act.action.atype)),
                        actdate=T(str(act.action.adate)),
                        docname=act.documents.title,
                        docurl='%s%s' % (urlbase,
                                                                 URL(r=request,
                                                                         f='store',
                                                                          args=act.documents.id)),
                        fileurl='%s%s' % (urlbase,
                                                                 URL(r=request,
                                                                         f='download',
                                                                          args=act.documents.file)) if act.documents.file else '')
        mailbody = string.Template(act.action.mbody).substitute(svars)
        if not mail.send(to=act.action.email,
                        subject=T('Automated email from DMS'),
                        message=mailbody):
            err += '\n' + T('Action email couldn\'t be send to %(name)',
                                dict(name=act.action.email))
        db(db.action.documents_id != 0)(db.action.id == act.action.id).update(done=True)

    return err



@auth.requires_login()
def index():
        import string
        dlist = None
        form = SQLFORM.factory(
                                Field('txt', 'string',
                                            label=T('Search for text')),
                                Field('tag', 'string',
                                            label=db.documents.tag.label),
                                        )
        if form.accepts(request.vars, keepvalues=True):
                dbquery = (db.documents.id > 0) & (db.documents.modified_by == db.auth_user.id) & \
                        ((db.documents.expire_on >= request.now) | (db.documents.expire_on == None))
                if form.vars.txt:
                        t = str(form.vars.txt)
                        t = t.decode('utf-8').lower().encode('utf-8')
                        dbquery &= ((db.documents.title.lower().like('%' + str(t) + '%')) | \
                                            (db.documents.comments.lower().like('%' + str(t) + '%')) | \
                                            (db.documents.body.lower().like('%' + str(t) + '%')))
                if form.vars.tag:
                        formtags = form.vars.tag.replace(', ', ',').lower().split(',')
                        formtags.sort()
                        form.vars.tag = string.join(formtags, '%')
                        dbquery &= (db.documents.tag.like('%' + str(form.vars.tag) + '%'))
                dlist = db(dbquery).select()
        return dict(form=form, dlist=dlist)


@auth.requires_login()
def recognize():
    if not request.args:
        session.flash = T('No image is choosen!')
        redirect(URL(r=request, f='scanner'))
    try:
        scanconfig = db(db.scannerconfig.auth_user_id == auth.user_id).select(limitby=(0, 1))[0]
    except:
        scanconfig = None
    try:
        config = db(db.config.id > 0).select(limitby=(0, 1))[0]
    except:
        config = None
    if not config:
        session.flash = T('No config for ocr!')
        redirect(URL(r=request, f='scanner'))

    if not scanconfig:
        lang = 'eng'
    else:
        lang = scanconfig.lang
    import string
    import os

    if request.vars.do == 'recognize':
        import subprocess
        scanname = session.scan[int(request.args(0))]['name_w_path']
        txtname = os.path.join(request.folder, 'private', session.scan[int(request.args(0))]['name'])
        rvars = dict(filefrom=scanname,
                            fileto=txtname,
                            lang=lang)
        cmd = config.ocr.split(' ')
        cmd = [string.Template(t).substitute(rvars) for t in cmd]
        proc = subprocess.Popen(cmd,
                                                                             stdout=subprocess.PIPE,
                                                                             stderr=subprocess.PIPE,
                                                                             universal_newlines=True,
                                                                             close_fds=True)
        proc.communicate()
        if proc.returncode:
            session.flash = XML(T('Something went wrong: %(err)s', dict(err='<br/>'.join(stderr))))
            redirect(URL(r=request, f='scanner'))
        else:
            if config.fileext:
                txtname = txtname + '.' + config.fileext
            txtfile = open(txtname, 'r')
            readlines = '\n'.join(txtfile.readlines())
            txtfile.close()
            os.unlink(txtname)
            session.scan[int(request.args(0))]['ocr'] = readlines
            redirect(URL(r=request, args=request.args, vars=dict(do='edit')))
    elif request.vars.do == 'delete':
        try:
            session.scan[int(request.args(0))]['ocr'] = None
            session.flash = T('Recognized text deleted')
        except:
            pass
        redirect(URL(r=request, f='scanner'))
    try:
        form = SQLFORM.factory(
                                                Field('text', 'text',
                                                label=T('Recognized text'),
                                                default=session.scan[int(request.args(0))]['ocr'],
                                                update=session.scan[int(request.args(0))]['ocr'],),
                                        )
        if form.accepts(request.vars, session):
            session.flash = T('Recognized text linked to the picture')
            redirect(URL(r=request, f='scanner'))
    except Exception, e:
        form = None

    return dict(form=form)


@auth.requires_login()
def scanning():
    if not session.scan:
        session.scan = []
    import os
    try:
            scanconfig = db(db.scannerconfig.auth_user_id == auth.user_id).\
                select(limitby=(0, 1)).first()
    except:
            scanconfig = None
            session.flash = T('There isn\'t any scanner configured!')
            return ''
    try:
            config = db(db.config.id > 0).select(limitby=(0, 1))[0]
    except:
             session.flash = T('There isn\'t any config defined!')
             return ''

    import time
    import subprocess
    import Image
    imagename = "scan-%s" % time.time()
    sfname = "%s.tif" % imagename
    scanfile = os.path.join(request.folder, 'static', sfname)
    cmd = [config.prgscanimage,
           '--format=tiff',
           '-d', str(scanconfig.device),
           '-p']
    if scanconfig.mode:
        cmd.append('--mode=%s' % str(scanconfig.mode))
    if scanconfig.resolution:
        cmd.append('--resolution=%s' % str(scanconfig.resolution))
    if scanconfig.size:
            papersize = db(db.papersize.id == scanconfig.size).select().first()
            cmd.extend(['-x', str(papersize.x), '-y', str(papersize.y)])
    if scanconfig.moreparams:
        cmd.extend(scanconfig.moreparams.split(' '))
    sf = open(scanfile, 'w')
    se = open("%s.err" % scanfile, 'w')
    proc = subprocess.Popen(cmd,
                            stdout=sf,
                            stderr=se,
                            universal_newlines=True,
                            close_fds=True)
    proc.communicate()
    sf.close()
    if proc.returncode:
            se = open("%s.err" % scanfile, 'r')
            e = string.join(se.readlines(), ' < br /> ')
            se.seek(0)
            session.flash = T('Error in scanning paper. Try again! [ %(error)s]',
                                             dict(error=str(e)))
            msg = DIV(P(T('Error in scanning paper. Try again!')),
                            P(string.join(se.readlines(), '<br/>')),
                            P(A(T('Try again'),
                                    _id='scanlink',
                                    _href='#',
                                    _class='btn')))
            se.close()
            os.unlink(scanfile)
            os.unlink("%s.err" % scanfile)
            return dict(msg=msg, form=form)
    os.unlink("%s.err" % scanfile)
    jpgname = "%s.jpg" % imagename
    thumbname = "%s-thumb.jpg" % imagename
    scanjpg = os.path.join(request.folder, 'static', jpgname)
    thumbjpg = os.path.join(request.folder, 'static', thumbname)
    try:
            i = Image.open(scanfile)
            i.save(scanjpg, 'JPEG')
            i.thumbnail((128, 500))
            i.save(thumbjpg)
            session.scan.append(dict(name_w_path=scanjpg,
                                                            name=jpgname,
                                                            thumb_w_path=thumbjpg,
                                                            thumb=thumbname,
                                                            ocr=None))
            msg = T('Page scan succeed!')
            msg = DIV(A(T('Delete scans'), _href=URL(r=request, f='scanner', vars=dict(delete=1))),
                    P(T('Page scan succeed!')),
                    P(A(T('Next scan'),
                            _id='scanlink',
                            _href='#',
                            _class='btn'
                            ), _style='text:center;'))
    except Exception, e:
            session.flash = T("Error in conversion: %(error)s", dict(error=str(e)))
            try:
                    os.unlink(scanjpg)
                    os.unlink(thumbjpg)
            except:
                    pass
    os.unlink(scanfile)
    return 'location.reload();'

@auth.requires_login()
def scanner():
    import os
    import Image
    db.scannerconfig.auth_user_id.default = auth.user_id
    if request.vars.delete:
            hiba = ""
            if request.vars.delete == 'all':
                    for s in session.scan:
                            try:
                                    os.unlink(s['name_w_path'])
                                    os.unlink(s['thumb_w_path'])
                            except Exception, e:
                                    hiba += " %s" % str(e)
                    if hiba == '':
                            session.flash = T('Scans deleted!')
                    else:
                            session.flash = "%s %s" % (str(T('Scans deleted but file deletion error:')), hiba)
                    session.scan = None
                    redirect(URL())
            else:
                    try:
                            os.unlink(session.scan[int(request.vars.delete)]['name_w_path'])
                            os.unlink(session.scan[int(request.vars.delete)]['thumb_w_path'])
                            session.scan.pop(int(request.vars.delete))
                    except Exception, e:
                            hiba += " %s" % str(e)
                    if hiba == '':
                            response.flash = T('%(num)s. scan deleted!', dict(num=str(int(request.vars.delete) + 1)))
                    else:
                            response.flash = "%s %s" % (str(T('Scans deleted but file deletion error:')), hiba)

    import re
    import string

    if session.scan:
            msg = DIV(A(T('Delete scans'),
                        _class='btn',
                        _href=URL(r=request,
                                  f='scanner',
                                  vars=dict(delete='all'))),
                            P(A(T('Next scan'),
                                    _id='scanlink',
                                    _href='#',
                                _class='btn',
                                _style='text:center;')))
    else:
            msg = DIV(P(A(T('Scan'),
                          _id='scanlink',
                          _href='#',
                          _class='btn')))
    re_no_scanner = re.compile('No scanners were identified')
    re_devices = re.compile("^[^\`]*\`(?P<device>[^\']*)\' \w+ \w+ (?P<name>.*)$")
    try:
            scanconfig = db(db.scannerconfig.auth_user_id == auth.user_id).select(limitby=(0, 1))[0]
    except:
            scanconfig = None
    try:
            config = db(db.config.id > 0).select(limitby=(0, 1))[0]
    except:
             session.flash = T('There isn\'t any config defined!')
             redirect(URL(r=request, c='jogok', f='config'))

    r = seged.runcommand([[config.prgscanimage, '-L']])
    if re_no_scanner.search(string.join(r['messages'][0], ' ')):
            scanners = None
            form = None
            response.flash = T('No scanners were identified!')
            #redirect(URL(r=request,f='index'))
    dev = []
    sname = []
    for s in r['messages'][0]:
            m = re_devices.match(s)
            if m:
                    dev.append(m.group('device'))
                    sname.append(m.group('name'))
    db.scannerconfig.device.requires = IS_IN_SET(dev, sname)
    db.scannerconfig.resolution.requires = IS_NULL_OR(
                            IS_IN_SET(config.resolution.split(','),
                            zero=T('Default')))
    if scanconfig:
            form = crud.update(db.scannerconfig, scanconfig.id, deletable=False)
    else:
            form = crud.create(db.scannerconfig)
    if not session.scan and not request.vars.scan:
            session.scan = []
            msg = DIV(P(T('Put the paper on the scanner!')),
                      P(A(T('Scan'),
                          _id='scanlink',
                          _href='#',
                          _class='btn')))
            return dict(msg=msg, form=form)

    return dict(msg=msg, form=form)


@auth.requires_login()
def storevalidate(form):
        import string
        formtags = form.vars.tag.replace(', ', ',').lower().split(',')
        formtags.sort()
        form.vars.tag = string.join(formtags, ',')

        if request.vars.source == 'scanner':
                import re
                import os
                p = form.vars.title.decode('utf-8').lower().encode('utf-8')
                p = p.replace('ö', 'o')
                p = p.replace('ü', 'u')
                p = p.replace('ó', 'o')
                p = p.replace('ő', 'o')
                p = p.replace('ú', 'u')
                p = p.replace('é', 'e')
                p = p.replace('á', 'a')
                p = p.replace('ű', 'u')
                p = p.replace('í', 'i')
                p = p.replace('ö', 'o')
                p = re.sub(r"[^\w]", "_", p)
                if len(session.scan) > 1:
                        import subprocess
                        filename = os.path.join(request.folder, 'static', ' % s.pdf' % p)
                        config = db(db.config.id > 0).select(limitby=(0, 1))
                        if not config:
                                session.flash = T('There isn\'t any config defined!')
                                redirect(URL(r=request, c='jogok', f='config'))
                        cmd = [config[0].prgconvert]
                        cmd.extend([n['name_w_path'] for n in session.scan])
                        cmd.extend(['-compress', 'zip', filename])
                        c = subprocess.Popen(cmd,
                                                             stdout=subprocess.PIPE,
                                                             stderr=subprocess.PIPE,
                                                             universal_newlines=True,
                                                             close_fds=True)
                        (stdout, stderr) = c.communicate()
                        try:
                                for df in session.scan:
                                        os.unlink(df['name_w_path'])
                                        os.unlink(df['thumb_w_path'])
                                session.scan = None
                        except:
                                # FIXME: errorhandling
                                pass
                        if c.returncode:
                                form.errors.title = T('Error in processing scanned files to pdf!<br/>%(error)s',
                                                                        dict(error=stderr))
                                return False
                else:
                        filename = os.path.join(request.folder, 'static', '%s.jpg' % p)
                        try:
                                os.rename(session.scan[0]['name_w_path'], filename)
                                os.unlink(session.scan[0]['thumb_w_path'])
                                session.scan = None
                        except Exception, e:
                                form.errors.title = T('Error renaming file!<br/>%(error)s',
                                                                        dict(error=str(e)))
                                return False
                if not form.errors:
                        form.vars.file = db.documents.file.store(open(filename))
                        try:
                                os.unlink(filename)
                        except:
                                # FIXME: errorhandling
                                pass

@auth.requires_login()
def populatetags(form):
        formtags = form.vars.tag.replace(', ', ',').lower().split(',')
        dbtags = [d.tag for d in db(db.tags.id > 0).select(db.tags.tag)]
        formtags = [u for u in formtags if dbtags.count(u) == 0]
        for tag in formtags:
                db.tags.insert(tag=tag)

@auth.requires_login()
def action():
    if not request.args:
        session.flash = T('No document selected')
        redirect(URL(r=request, f='index'))
    db.action.documents_id.default = request.args(0)
    db.action.documents_id.writable = False
    if int(request.args(0)) == 0:
        form = crud.update(db.action, request.args(1),
                                        onaccept=crud.archive ,
                                        deletable=False,
                                        )
    else:
        form = crud.update(db.action, request.args(1),
                                        onaccept=crud.archive ,
                                        deletable=False,
                                        next=URL(r=request, f='store', args=request.args(0)))
    db.action.documents_id.writable = True
    actionlist = db(db.action.documents_id == request.args(0)).select()
    return dict(form=form , actionlist=actionlist)

@auth.requires_login()
def store():
        templateform = SQLFORM.factory(
                                                                 Field('template', db.templates,
                                                                             label=T('Document template'),
                                                                             requires=IS_NULL_OR(IS_IN_DB(db, db.templates.id, '%(dgroup)s-> %(name)s', groupby=db.templates.dgroup | db.templates.name | db.templates.id))),
                                                                 )
        actionlist = None
        if not request.args:
                if request.vars.source == 'scanner':
                        db.documents.file.writable = False
                        db.documents.file.readable = False
                        body = ''
                        for image in session.scan:
                            if image['ocr']:
                                body += '\n%s' % image['ocr']
                            if len(body) > 0:
                                db.documents.body.default = body
                                db.documents.body.update = body
                form = crud.create(db.documents, onvalidation=storevalidate,
                                                 onaccept=lambda form:(populatetags(form), doaction(form, 'new')))
        else:
                if request.vars.source == 'scanner':
                        db.documents.file.writable = False
                        db.documents.file.readable = False
                else:
                    actionlist = db((db.action.done != True) &
                                                    (db.documents.id == db.action.documents_id) &
                                                     (db.action.documents_id == request.args(0)) &
                                                      ((db.action.adate >= request.now) | (
                                                      (db.documents.expire_on >= request.now) &
                                                      (db.action.adate == None)))
                                                      ).select(
                                                                                                                        orderby=db.action.adate)
                form = crud.update(db.documents, request.args(0), deletable=False,
                                                 onvalidation=storevalidate,
                                                 onaccept=lambda form: (populatetags(form),
                                                                                                     crud.archive(form),
                                                                                                     doaction(form, 'modified')))
        if request.vars.source == 'scanner':
                db.documents.file.writable = True
                db.documents.file.readable = True
        return dict(form=form, templateform=templateform , actionlist=actionlist)

@auth.requires_login()
def mailto():
    if not request.args:
        session.flash = T('No document selected')
        redirect(URL(r=request, f='index'))
    doc = db(db.documents.id == request.args(0)).select().first()
    if not doc:
        session.flash = T('Document not found')
        redirect(URL(r=request, f='index'))
    form = SQLFORM.factory(
                                            Field('email', 'string',
                                                    label=T('E-mail'),
                                                    requires=IS_EMAIL()),
                                            Field('subject', 'string',
                                                    label=T('Subject'),
                                                    requires=IS_NOT_EMPTY(),
                                                    default=T('DMS document')),
                                            Field('body', 'text',
                                                    label=T('Body'),
                                                    requires=IS_NOT_EMPTY(),
                                                    ),
                                            )
    if form.accepts(request.vars, session):
        pass
    return dict(form=form)

@auth.requires_login()
def search():
        import string
        dlist = None
        form = SQLFORM.factory(
                                Field('title', 'string',
                                            label=db.documents.title.label),
                                Field('tag', 'string',
                                            label=db.documents.tag.label),
                                Field('body', 'string',
                                            label=db.documents.body.label),
                                Field('comments', 'string',
                                            label=db.documents.comments.label),
                                Field('expired', 'boolean',
                                            label=T('Expired'),
                                            default=False),
                                Field('expire_after', 'date',
                                            label=T('Expire after'),
                                            requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d')))),
                                Field('expire_before', 'date',
                                            label=T('Expire before'),
                                            requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d')))),
                                Field('created_by', db.auth_user,
                                            requires=IS_NULL_OR(IS_IN_DB(db, 'auth_user.id', '%(last_name)s %(first_name)s')),
                                            label=db.documents.created_by.label),
                                Field('created_after', 'date',
                                            label=T('Created after'),
                                            requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d')))),
                                Field('created_before', 'date',
                                            label=T('Created before'),
                                            requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d')))),
                                Field('modified_by', db.auth_user,
                                            requires=IS_NULL_OR(IS_IN_DB(db, 'auth_user.id', '%(last_name)s %(first_name)s')),
                                            label=db.documents.modified_by.label),
                                Field('modified_after', 'date',
                                            label=T('Last modified after'),
                                            requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d')))),
                                Field('modified_before', 'date',
                                            label=T('Last modified before'),
                                            requires=IS_NULL_OR(IS_DATE(format=T('%Y-%m-%d')))),
                                                 )
        if form.accepts(request.vars, keepvalues=True):
                dbquery = (db.documents.id > 0) & (db.documents.modified_by == db.auth_user.id)
                if form.vars.title:
                        t = str(form.vars.title)
                        t = t.decode('utf-8').lower().encode('utf-8')
                        dbquery &= (db.documents.title.lower().like('%' + str(t) + '%'))
                if form.vars.body:
                        t = str(form.vars.body)
                        t = t.decode('utf-8').lower().encode('utf-8')
                        dbquery &= (db.documents.body.lower().like('%' + str(t) + '%'))
                if form.vars.comments:
                        t = str(form.vars.comments)
                        t = t.decode('utf-8').lower().encode('utf-8')
                        dbquery &= (db.documents.comments.lower().like('%' + str(t) + '%'))
                if not form.vars.expire_after and not form.vars.expire_before:
                        if form.vars.expired:
                                dbquery &= (db.documents.expire_on <= request.now)
                        else:
                                dbquery &= ((db.documents.expire_on >= request.now) | \
                                                    (db.documents.expire_on == None))
                if form.vars.expire_after:
                        dbquery &= (db.documents.expire_on >= form.vars.expire_after)
                if form.vars.expire_before:
                        dbquery &= (db.documents.expire_on <= form.vars.expire_before)
                if form.vars.created_by:
                        dbquery &= (db.documents.created_by == form.vars.created_by)
                if form.vars.created_after:
                        dbquery &= (db.documents.created_on >= form.vars.created_after)
                if form.vars.created_before:
                        dbquery &= (db.documents.created_on <= form.vars.created_before)
                if form.vars.modified_by:
                        dbquery &= (db.documents.modified_by == form.vars.modified_by)
                if form.vars.modified_after:
                        dbquery &= (db.documents.modified_on >= form.vars.modified_after)
                if form.vars.modified_before:
                        dbquery &= (db.documents.modified_on <= form.vars.modified_before)
                if form.vars.tag:
                        formtags = form.vars.tag.replace(', ', ',').lower().split(',')
                        formtags.sort()
                        form.vars.tag = string.join(formtags, '%')
                        dbquery &= (db.documents.tag.like('%' + str(form.vars.tag) + '%'))
                dlist = db(dbquery).select()
        return dict(form=form, dlist=dlist)

@auth.requires_login()
def templates():
        form = crud.update(db.templates, request.args(0), onaccept=crud.archive)
        tlist = db(db.templates.id > 0).select(orderby=db.templates.dgroup | db.templates.name)
        return dict(form=form, tlist=tlist)

def user():
        """
        exposes:
        http://..../[app]/default/user/login
        http://..../[app]/default/user/logout
        http://..../[app]/default/user/register
        http://..../[app]/default/user/profile
        http://..../[app]/default/user/retrieve_password
        http://..../[app]/default/user/change_password
        use @auth.requires_login()
                @auth.requires_membership('group name')
                @auth.requires_permission('read','table name',record_id)
        to decorate functions that need access control
        """
        return dict(form=auth())

def x():
        return dict()

def download():
        """
        allows downloading of uploaded files
        http://..../[app]/default/download/[filename]
        """
        return response.download(request, db)


def call():
        """
        exposes services. for example:
        http://..../[app]/default/call/jsonrpc
        decorate with @services.jsonrpc the functions to expose
        supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
        """
        session.forget()
        return service()
