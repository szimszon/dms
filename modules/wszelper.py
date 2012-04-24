#!/usr/bin/env python
#-*- coding: utf-8 -*-

class WSzelper( object ):
  '''
    Közös segítő funkciók
  '''
  def __init__( self, globals, db ):
    self.db=db
    self.globals=globals
    self.session=self.globals['session']
    self.request=self.globals['request']
    self.response=self.globals['response']
    self.verzion="2010032501"

  def flushtrace( self ):
    '''
      Visszalépés feljegyzések törlése
    '''
    self.session.backstep=list()

  def dotrace( self ):
    '''
      Aktuális lap feljegyzése a visszatéréshez
    '''
    if not self.session.backstep:
      self.session.backstep=list()
    if ( len( self.request.args )>0 ):
      if ( self.request.args[0]=='f' ):
        self.flushtrace()
    url=str( self.globals['URL']( r = self.request,
                                          args = self.request.args,
                                          vars = self.request.get_vars ) )
    # ha most tértünk vissza az oldalra, akkor az előző oldal bejegyzését törlni kell
    # ebben az esetben a listában már szerepel
    try:
      urlnow=url
      self.session.backstep=self.session.backstep[:self.session.backstep.index( urlnow )+1]
    except:
      pass
    # itt mi vagyunk az utolso tag, meg kell akadalyozni, hogy tobbszor
    # bekeruljon, de nem vesszuk ki
    try:
      urlnow="^%s"%self.request.url
      reurl="^%s"%self.session.backstep[-1:][0]
      #self.response.flash="[%s][%s][%s]"%( url, urlnow, reurl )
      if ( reurl.count( urlnow )==0 ):
        self.session.backstep.append( url )
      else:
        self.session.backstep[len( self.session.backstep )-1]=str( url )
    except Exception, e:
      self.session.backstep.append( url )

  def backstep( self ):
    '''
      Az előző feljegyzett oldal uself.request.args-je
    '''
    try:
      bs=str( self.session.backstep[-2:][0] )
      if ( len( bs )==0 ):
        bs=None
    except:
      bs=None
    return bs

  def runcommand(self,command):
    """
    >>> x=dict(session=None,request=None,response=None)
    >>> s=WSzelper(x,None)
    >>> c=[]
    >>> c.append(['/bin/echo','egy'])
    >>> c.append(['/bin/echo','ketto'])
    >>> c.append(['/bin/sleep','5'])
    >>> c.append(['/bin/echo','harom'])
    >>> s.runcommand(c)
    {'messages': [['egy\\n'], ['ketto\\n'], [], ['harom\\n']], 'errorcodes': [0, 0, 0, 0], 'returncode': True, 'errormessages': [None, None, None, None]}
    """
    import subprocess
    returncode=True
    errorcodes=[]
    messages=[]
    errormessages=[]
    if not isinstance(command,(list,tuple)):
        command=[command]
    procs=[]
    for com in command:
      procs.append(subprocess.Popen( com,
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.PIPE,
                                 universal_newlines = True,
                                 close_fds = True ))
    for p in procs:
      p.wait()
      errorcodes.append(p.returncode)
      if ( p.returncode<>0 ):
        errormessages.append(list(p.stderr.readlines()))
        returncode=False
      else:
        errormessages.append(None)
      messages.append(list(p.stdout.readlines()))
    return dict(returncode=returncode,
          errorcodes=errorcodes,
          messages=messages,
          errormessages=errormessages)

if __name__ == "__main__":
    import doctest
    doctest.testmod()