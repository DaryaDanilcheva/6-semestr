# -*- coding: utf-8 -*-

import os, csv

import telephonedir

def save(telephoneDir):
  def write(subdivision):
    for s in subdivision.subdivisions:
      writer.writerow((s.name, subdivision.name))
      write(s)

  writer = csv.writer(open(os.path.join(os.curdir, 'subdivision.csv'), 'wb'), delimiter=';')
  writer.writerow((telephoneDir.subdivision.name, None))
  write(telephoneDir.subdivision)

  def find(c, subdivision):
    if c in subdivision.collaborators:
      return subdivision.name
    else:
      for s in subdivision.subdivisions:
        r = find(c, s)
        if r:
          return r

  writer = csv.writer(open(os.path.join(os.curdir, 'su.csv'), 'wb'), delimiter=';')
  for r in telephoneDir:
    writer.writerow((r.telephone.number, r.collaborator.code, r.collaborator.family, r.collaborator.name, r.collaborator.patronym, find(r.collaborator, telephoneDir.subdivision), r.telephone.type.name))

def load():
  subdivision = {}
  for rec in csv.reader(open(os.path.join(os.curdir, 'subdivision.csv'), 'rb'), delimiter=';'):
    subdivision[rec[0]] = telephonedir.Subdivision(rec[0])
    if rec[1]:
      subdivision[rec[1]].addSubdivision(subdivision[rec[0]])
    else:
      telephoneDir = telephonedir.TelephoneDir(telephonedir.Telephones(telephonedir.TelephoneTypes()), subdivision[rec[0]])

  telephones, telephoneTypes, collaborators = {}, {}, {}
  for rec in csv.reader(open(os.path.join(os.curdir, 'ssu.csv'), 'rb'), delimiter=';'):
    if rec[6] not in telephoneTypes:
      telephoneTypes[rec[6]] = telephonedir.TelephoneType(rec[6])
      telephoneDir.telephones.telephoneTypes.add(telephoneTypes[rec[6]])
    if rec[0] not in telephones:
      telephones[rec[0]] = telephonedir.Telephone(rec[0], telephoneTypes[rec[6]])
      telephoneDir.telephones.add(telephones[rec[0]])
    key = int(rec[1])
    if key not in collaborators:
      collaborators[key] = telephonedir.Collaborator(key, rec[2], rec[3], rec[4])
      subdivision[rec[5]].add(collaborators[key])
    telephoneDir.add(telephonedir.TelephoneRecord(telephones[rec[0]], collaborators[key]))

  return telephoneDir

if __name__ == '__main__':
  telephoneDir = load()

  for s in telephoneDir.subdivision.iterSubdivision():
    #if s.name == 'помощник проректора':
    for r in telephoneDir:
      if r.collaborator in s:
	print r.telephone.number, "%s %s. %s. %s."% \
	        (r.collaborator.family, r.collaborator.name[:2], r.collaborator.patronym[:2], s.name)
      #  break
'''
  for s in telephoneDir.subdivision.iterSubdivision():
    if s.name == 'зав. кафедрой':
      for r in telephoneDir:
        if r.collaborator in s and r.collaborator.family.find('сс') >= 0:
          print r.telephone.number, "%s %s. %s."% \
                (r.collaborator.family, r.collaborator.name[:2], r.collaborator.patronym[:2])
      break
'''
save(telephoneDir)
