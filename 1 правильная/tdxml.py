# -*- coding: utf-8 -*-

import os
from xml.dom import minidom
import xml.sax

import telephonedir

def save(telephoneDir):
  dom = minidom.Document()
  td = dom.createElement(u"telephonedir1")
  dom.appendChild(td)

  def insert(subdivision, el):
    sel = dom.createElement(u"Подразделение")
    el.appendChild(sel)
    sel.setAttribute(u"название", subdivision.name.decode('utf-8'))
    for c in subdivision.collaborators:
      cel = dom.createElement(u"Сотрудник")
      sel.appendChild(cel)
      cel.setAttribute(u"кодСотрудника", str(c.code))
      cel.setAttribute(u"фамилия", c.family.decode('utf-8'))
      cel.setAttribute(u"имя", c.name.decode('utf-8'))
      cel.setAttribute(u"отчество", c.patronym.decode('utf-8'))
    for s in subdivision.subdivisions:
      insert(s, sel)

  insert(telephoneDir.subdivision, td)

  tt = dom.createElement(u"ТелефоновТипы")
  td.appendChild(tt)
  codeTelephoneType, telephoneTypes = 1, {}
  for t in telephoneDir.telephones.telephoneTypes:
    tel = dom.createElement(u"ТелефонаТип")
    tt.appendChild(tel)
    tel.setAttribute(u"кодТелефонаТип", str(codeTelephoneType))
    tel.setAttribute(u"название", t.name.decode('utf-8'))
    telephoneTypes[t] = codeTelephoneType
    codeTelephoneType += 1

  tt = dom.createElement(u"Телефоны")
  td.appendChild(tt)
  codeTelephone, telephones = 1, {}
  for t in telephoneDir.telephones:
    tel = dom.createElement(u"Телефон")
    tt.appendChild(tel)
    tel.setAttribute(u"кодТелефона", str(codeTelephone))
    tel.setAttribute(u"кодТелефонаТип", str(telephoneTypes[t.type]))
    tel.setAttribute(u"номер", t.number.decode('utf-8'))
    telephones[t] = codeTelephone
    codeTelephone += 1

  tt = dom.createElement(u"ТелефонныйСправочник")
  td.appendChild(tt)
  for r in telephoneDir:
    tel = dom.createElement(u"Запись")
    tt.appendChild(tel)
    tel.setAttribute(u"кодТелефона", str(telephones[r.telephone]))
    tel.setAttribute(u"кодСотрудника", str(r.collaborator.code))

  open(os.path.join(os.curdir, "telephonedir.xml"), "w").write(dom.toprettyxml(encoding='utf-8', indent=' '*2))

def load():
  class Handler(xml.sax.handler.ContentHandler):
    def __init__(self):
      xml.sax.handler.ContentHandler.__init__(self)
      self.subdivisions = []
      self.collaborators = {}
      self.telephoneTypes = {}
      self.telephones = {}

    def startElement(self, name, attr):
      global telephoneDir
      if name == u'Подразделение':
        subdivision = telephonedir.Subdivision(attr.getValue(u'название').encode('utf-8'))
        if self.subdivisions:
          self.subdivisions[-1].addSubdivision(subdivision)
        self.subdivisions.append(subdivision)
      elif name == u'Сотрудник':
        collaborator = telephonedir.Collaborator(int(attr.getValue(u'кодСотрудника')),\
                                                  attr.getValue(u'фамилия').encode('utf-8'),\
                                                  attr.getValue(u'имя').encode('utf-8'),\
                                                  attr.getValue(u'отчество').encode('utf-8'))
        self.subdivisions[-1].add(collaborator)
        self.collaborators[collaborator.code] = collaborator
      elif name == u'ТелефонаТип':
        self.telephoneTypes[int(attr.getValue(u'кодТелефонаТип'))] = \
                            telephonedir.TelephoneType(attr.getValue(u'название').encode('utf-8'))
      elif name == u'Телефон':
        t = telephonedir.Telephone(attr.getValue(u'номер'), self.telephoneTypes[int(attr.getValue(u'кодТелефонаТип'))])
        self.telephones[int(attr.getValue(u'кодТелефона'))] = t
      elif name == u'ТелефонныйСправочник':
        telephoneDir = telephonedir.TelephoneDir(telephonedir.Telephones(telephonedir.TelephoneTypes()),\
                                                 self.subdivisions[0])
        for t in self.telephoneTypes.itervalues():
          telephoneDir.telephones.telephoneTypes.add(t)
        for t in self.telephones.itervalues():
          telephoneDir.telephones.add(t)
      elif name == u'Запись':
        r = telephonedir.TelephoneRecord(self.telephones[int(attr.getValue(u'кодТелефона'))],
                                         self.collaborators[int(attr.getValue(u'кодСотрудника'))])
        telephoneDir.add(r)

  parser = xml.sax.make_parser()
  parser.setContentHandler(Handler())
  parser.parse(os.path.join(os.curdir, "telephonedir.xml"))

  return telephoneDir

if __name__ == '__main__':
  telephoneDir = load()

  for s in telephoneDir.subdivision.iterSubdivision():
    if s.name == 'помощник проректора':
      for r in telephoneDir:
        if r.collaborator in s and r.collaborator.family.find('ск') >= 0:
          print r.telephone.number, "%s %s. %s."% \
                (r.collaborator.family, r.collaborator.name[:2], r.collaborator.patronym[:2])
      break

  for s in telephoneDir.subdivision.iterSubdivision():
    if s.name == 'зав. кафедрой':
      for r in telephoneDir:
        if r.collaborator in s and r.collaborator.family.find('сс') >= 0:
          print r.telephone.number, "%s %s. %s."% \
                (r.collaborator.family, r.collaborator.name[:2], r.collaborator.patronym[:2])
      break
