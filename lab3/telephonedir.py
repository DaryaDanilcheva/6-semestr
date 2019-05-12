# -*- coding: utf-8 -*-

"""
Телефонная книга организации
"""

import itertools

class Collaborator:
  """
  Сотрудник
  """
  def __init__(self, code, family, name, patronym):
    self.code = code
    self.family = family
    self.name = name
    self.patronym = patronym

  def __str__(self):
    return "%s %.2s. %.2s." % (self.family, self.name, self.patronym)

  def __hash__(self):
    return hash(self.code)

  def __eq__(self, other):
    return self.code == other.code

class Subdivision:
  """
  Подразделение
  """
  def __init__(self, name):
    self.name = name
    self.collaborators = set()
    self.subdivisions = set()

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    return self.name == other.name

  def __iter__(self):
    i = iter(self.collaborators)
    for s in self.subdivisions:
      i = itertools.chain(i, iter(s))
    return i

  def add(self, collaborator):
    assert collaborator not in self
    self.collaborators.add(collaborator)

  def addSubdivision(self, subdivision):
    assert subdivision not in self.subdivisions
    assert not set(self).intersection(set(subdivision))
    self.subdivisions.add(subdivision)

  def iterSubdivision(self):
    i = iter(self.subdivisions)
    for s in self.subdivisions:
      i = itertools.chain(i, s.iterSubdivision())
    return i

class TelephoneType:
  """
  Тип телефона
  """
  def __init__(self, name):
    self.name = name

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    return self.name == other.name

class TelephoneTypes(set):
  """
  Типы телефонов
  """
  def add(self, telephoneType):
    assert telephoneType not in self
    set.add(self, telephoneType)

class Telephone:
  """
  Телефон
  """
  def __init__(self, telephone, telephoneType):
    self.number = telephone
    self.type = telephoneType

  def __hash__(self):
    return hash(self.number)

  def __eq__(self, other):
    return self.number == other.number

class Telephones(set):
  """
  Телефоны
  """
  def __init__(self, telephoneTypes):
    set.__init__(self)
    self.telephoneTypes = telephoneTypes

  def add(self, telephone):
    assert telephone not in self
    assert telephone.type in self.telephoneTypes
    set.add(self, telephone)

class TelephoneRecord:
  """
  Запись в телефонном справочнике
  """
  def __init__(self, telephone, collaborator):
    self.telephone = telephone
    self.collaborator = collaborator

  def __hash__(self):
    return hash((self.telephone, self.collaborator))

  def __eq__(self, other):
    return self.telephone == other.telephone and \
           self.collaborator == other.collaborator

class TelephoneDir(set):
  """
  Телефонный справочник
  """
  def __init__(self, telephones, subdivision):
    set.__init__(self)
    self.telephones = telephones
    self.subdivision = subdivision

  def add(self, telephoneRecord):
    assert telephoneRecord.telephone in self.telephones
    assert telephoneRecord.collaborator in self.subdivision
    assert telephoneRecord not in self
    set.add(self, telephoneRecord)

if __name__ == '__main__':
  import tdcsv

  telephoneDir = tdcsv.load()

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
