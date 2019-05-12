# -*- coding: utf-8 -*-

"""
Web интерфейс телефонной книги
"""

import os
import hashlib, uuid
from Cheetah.Template import Template
import cherrypy
from cherrypy.lib import sessions
import hashlib, uuid
import tdods

class Root:
  @staticmethod
  def prepare(telephoneDir):
    Root.collaborators = list(sorted(telephoneDir.subdivision))
    Root.subdivisions = list(sorted(telephoneDir.subdivision.iterSubdivision()))
    Root.subdivisions.insert(0, 'все')
    Root.telephoneTypes = list(sorted(telephoneDir.telephones.telephoneTypes))
    Root.telephoneTypes.insert(0, 'все')
    Root.telephoneDir = list(sorted(telephoneDir))

  @cherrypy.expose
  def check(self, login='', password=''):
    salt = uuid.uuid4().hex
    users = {'log':hashlib.sha512('admin' + salt).hexdigest()}

    login = login.encode('utf-8')
    password = hashlib.sha512(password.encode('utf-8') + salt).hexdigest()

    if cherrypy.session.get('login', None) == 'log':
      raise cherrypy.HTTPRedirect('/database/')
    else:
      if login == "log" and password == users[login]:
        cherrypy.session['login'] = login
        raise cherrypy.HTTPRedirect('/database/')
      else:
        return "wrong login or password" 

  @cherrypy.expose
  def close_session(self):
    cherrypy.session.pop('login', None)
    raise cherrypy.HTTPRedirect('/')

  @cherrypy.expose
  def index(self, num=None):
    if cherrypy.session.get('login', None) == 'login':
      raise cherrypy.HTTPRedirect('/database/')
    else:
      userForm = Template(file=os.path.join(os.curdir, 'index.tmpl')) 
      return str(userForm)  

  @cherrypy.expose
  def database(self, page='0', subdivision='0', collaborator='', number='', telephoneType='0'):
    page = int(page)
    subdivision = int(subdivision)
    telephoneType = int(telephoneType)
    collaborator = collaborator.encode('utf-8')
    number = number.encode('utf-8')
    if not subdivision:
      lambdaSubdivision = lambda rec: True
    else:
      subdivisions = list(sorted(telephoneDir.subdivision.iterSubdivision()))
      subdivisions.insert(0, 'все')
      s = Root.subdivisions[subdivision]
      lambdaSubdivision = lambda rec: rec.collaborator in s
    if not collaborator:
      lambdaCollaborator = lambda rec: True
    else:
      lambdaCollaborator = lambda rec: str(rec.collaborator)[0:len(collaborator)] == collaborator
    if not number:
      lambdaNumber = lambda rec: True
    else:
      lambdaNumber = lambda rec: str(rec.telephone.number)[0:len(number)] == number
    if not telephoneType:
      lambdaTelephoneType = lambda rec: True
    else:
      telephoneTypes = list(sorted(telephoneDir.telephones.telephoneTypes))
      telephoneTypes.insert(0, 'все')
      t = Root.telephoneTypes[telephoneType]
      lambdaTelephoneType = lambda rec: rec.telephone.type == t
    tmpDir = list(sorted(telephoneDir))
    tmpDir = filter(lambda telephone: lambdaSubdivision(telephone) and \
                                                    lambdaCollaborator(telephone) and \
                                                    lambdaNumber(telephone) and \
                                                    lambdaTelephoneType(telephone), tmpDir)


  
    root = Template(file=os.path.join(os.curdir, 'base.tmpl'))
      #root = Template(file=os.path.join(os.curdir, 'index.tmpl'))
    root.page = page
    root.subdivision = subdivision
    root.subdivisions = Root.subdivisions
    root.collaborator = collaborator
    root.number = number
    root.telephoneType = telephoneType
    root.telephoneTypes = Root.telephoneTypes
    #root.telephoneDir = tmpDir

    tmpDir = filter(lambda telephone: lambdaSubdivision(telephone) and \
                                                 lambdaCollaborator(telephone) and \
                                                 lambdaNumber(telephone) and \
                                                 lambdaTelephoneType(telephone), Root.telephoneDir)

    root.telephoneDir = tmpDir
    namesList = []
    phonesList = []
    typeList = []
    proffession = []
    workList = []

    '''
    for r in tmpDir:
    row((r.telephone.number, r.collaborator.code, r.collaborator.family.decode("utf-8"), r.collaborator.name.decode("utf-8"), r.collaborator.patronym.decode("utf-8"), find(r.collaborator, telephoneDir.subdivision)))
    '''
    def find(c, subdivision):
      if c in subdivision.collaborators:
        return subdivision.name.decode("UTF-8")
      else:
        for s in subdivision.subdivisions:
          r = find(c, s)
          if r:
            return r

    for rr in tmpDir:
      namesList.append(rr.collaborator.family.decode("utf-8")+ ' '+ rr.collaborator.name.decode("utf-8") + ' ' +rr.collaborator.patronym.decode("utf-8"))
      phonesList.append(rr.telephone.number)
      typeList.append(rr.telephone.type.name.decode("utf-8"))
      proffession.append(find(rr.collaborator, telephoneDir.subdivision))
      workList.append(tdcsv.find2(tdcsv.find(rr.collaborator, telephoneDir.subdivision)))

    root.namesList = namesList
    root.phonesList = phonesList
    root.typeList = typeList
    root.proffession = proffession
    root.workList = workList

    lst = []
    for s in telephoneDir.subdivision.iterSubdivision():
        #if s.name == 'помощник проректора':
        for r in telephoneDir:
            #if r.collaborator in s: #and r.collaborator.family.find('ск') >= 0:
          lst.append(tdcsv.find(r.collaborator, telephoneDir.subdivision))
        break
    root.col = lst

      # print('!!!!!!!!!!!!!!!!!!!!!!!!!!')
      # print(len(lst))
      # root.lnln = len(lst)

    workplace = []
    for s in telephoneDir.subdivision.iterSubdivision():
      #if s.name == 'помощник проректора':
        for r in telephoneDir:
          #if r.collaborator in s: #and r.collaborator.family.find('ск') >= 0:
          workplace.append(tdcsv.find2(tdcsv.find(r.collaborator, telephoneDir.subdivision)))
        break
    root.wplist = workplace

    return str(root)

  @cherrypy.expose
  def export(self, subdivision='0', collaborator='', number='', telephoneType='0'):
    if not cherrypy.session.get('login', None):
      raise cherrypy.HTTPRedirect('/login')
    subdivision = int(subdivision)
    telephoneType = int(telephoneType)
    collaboratorR = collaborator.encode('utf-8')
    number = number.encode('utf-8')
    tdods.save(telephoneDir, subdivision, collaboratorR, number, telephoneType)
    basename = os.path.basename('telephonedir.ods')
    localDir = os.path.dirname(__file__)
    absDir = os.path.join(os.getcwd(), localDir)
    filename = os.path.join(absDir, basename)
    mime     = 'application/x-download'
    return cherrypy.lib.static.serve_file(filename, mime, basename)

root = Root()

cherrypy.config.update({
  'log.screen': True,
  'environment': 'production',
  'server.socket_port': 8080,
  'server.threadPool':10,
  'tools.staticfile.on': False,
  'tools.sessions.on': True,
  'tools.sessions.timeout': 60,
})

conf = {
  '/style.css': {
    'tools.staticfile.on': True,
    'tools.staticfile.filename': os.path.join(os.getcwd(), 'style.css'),
  },
}

def run(telephoneDir):
  Root.prepare(telephoneDir)
  cherrypy.tree.mount(root, config=conf)
  cherrypy.quickstart(Root(), '/', conf)
  cherrypy.engine.start()

if __name__ == '__main__':
  import tdcsv
  #os.system("fuser -k 8080/tcp")
  telephoneDir = tdcsv.load()
  run(telephoneDir)


