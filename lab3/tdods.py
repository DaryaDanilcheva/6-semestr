# -*- coding: utf-8 -*-

from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

def save(telephoneDir, subdivision, collaborator, number, telephoneType):
  textdoc = OpenDocumentSpreadsheet()

  tablecontents = Style(name="Table Contents", family="paragraph")
  tablecontents.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
  textdoc.styles.addElement(tablecontents)

  style2 = Style(name="style2", family="table-column")
  style2.addElement(TableColumnProperties(columnwidth="2cm"))
  textdoc.automaticstyles.addElement(style2)

  style6 = Style(name="style6", family="table-column")
  style6.addElement(TableColumnProperties(columnwidth="6cm"))
  textdoc.automaticstyles.addElement(style6)

  table = Table(name=u"Подразделения")
  table.addElement(TableColumn(numbercolumnsrepeated=2,stylename=style6))

  def row(rec):
    tr = TableRow()
    table.addElement(tr)
    for r in rec:
      tc = TableCell()
      tr.addElement(tc)
      p = P(stylename=tablecontents,text=r)
      tc.addElement(p)

  row((u"подразделение", u"головное подразделение"))
  row((telephoneDir.subdivision.name.decode("utf-8"), ""))

  def write(subdivision):
    for s in subdivision.subdivisions:
      row((s.name.decode("utf-8"), subdivision.name.decode("utf-8")))
      write(s)

  write(telephoneDir.subdivision)

  textdoc.spreadsheet.addElement(table)

  table = Table(name=u"Телефонный справочник")
  table.addElement(TableColumn(numbercolumnsrepeated=2,stylename=style2))
  table.addElement(TableColumn(numbercolumnsrepeated=4,stylename=style6))

  row((u"телефон", u"код сотр.", u"фамилия", u"имя", u"отчество", u"подразделение"))

  def find(c, subdivision):
    if c in subdivision.collaborators:
      return subdivision.name.decode("UTF-8")
    else:
      for s in subdivision.subdivisions:
        r = find(c, s)
        if r:
          return r

  subdivision = int(subdivision)
  telephoneType = int(telephoneType)
  collaborator = collaborator.decode('utf-8')
  number = number.encode('utf-8')
  if not subdivision:
    lambdaSubdivision = lambda rec: True
  else:
    subdivisions = list(sorted(telephoneDir.subdivision.iterSubdivision()))
    subdivisions.insert(0, 'все')
    s = subdivisions[subdivision]
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
    t = telephoneTypes[telephoneType]
    lambdaTelephoneType = lambda rec: rec.telephone.type == t
  tmpDir = list(sorted(telephoneDir))
  tmpDir = filter(lambda telephone: lambdaSubdivision(telephone) and \
                                                   lambdaCollaborator(telephone) and \
                                                   lambdaNumber(telephone) and \
                                                   lambdaTelephoneType(telephone), tmpDir)
  print subdivision, telephoneType, collaborator, number
  for r in tmpDir:
    row((r.telephone.number, r.collaborator.code, r.collaborator.family.decode("utf-8"), r.collaborator.name.decode("utf-8"), r.collaborator.patronym.decode("utf-8"), find(r.collaborator, telephoneDir.subdivision)))

  textdoc.spreadsheet.addElement(table)
  textdoc.save("telephonedir.ods")

if __name__ == '__main__':
  import tdcsv

  telephoneDir = tdcsv.load()
  #save(telephoneDir)
