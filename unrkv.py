#!/usr/bin/env python

import argparse
import struct
import sys
import traceback

HEADER = [
  'I fileCount',
  ]
ENTRY = [
  'I nameOffset',
  'I', # zero
  'I size',
  'I offset',
  'I', # checksum?
  ]

#------------------------------------------------------------------------------
class Struct(object):
  #----------------------------------------------------------------------------
  def __init__(self, fields, source):
    fieldNames = [f[1:].strip() for f in fields]
    self._fieldNames = [f for f in fieldNames if len(f)]

    layout = '<' + ''.join([f[0] for f in fields])
    size = struct.calcsize(layout)
    values = struct.unpack(layout, source.read(size))

    for i in xrange(len(fields)):
      if len(fieldNames[i]):
        setattr(self, fieldNames[i], values[i])

  #----------------------------------------------------------------------------
  def __repr__(self):
    fields = ['%r: %r' % (n, getattr(self, n)) for n in self._fieldNames]
    return '{ ' + ', '.join(fields) + ' }'

#------------------------------------------------------------------------------
def readStr(source):
  result = ''
  while True:
    c = source.read(1)
    if len(c) == 0 or c[0] == '\0':
      return result
    result += c[0]

#------------------------------------------------------------------------------
def unpack(archive, extract=True):
  fingerprint = archive.read(4)
  if fingerprint != 'RKV2':
    raise IOError('not an RKV archive')

  header = Struct(HEADER, archive)
  print header

  files = []
  archive.seek(0x80)
  for n in xrange(header.fileCount):
    files.append(Struct(ENTRY, archive))

  nameBase = archive.tell()
  for f in files:
    archive.seek(nameBase + f.nameOffset)
    name = readStr(archive)
    print '  ... %s' % name

    if extract:
      archive.seek(f.offset)
      data = archive.read(f.size)
      with open(name, 'wb') as of:
        of.write(data)

  print '  %i files' % len(files)

#------------------------------------------------------------------------------
def main():
  parser = argparse.ArgumentParser()

  parser.add_argument('archive', nargs='+',
                      help='archive file(s) to extract')

  parser.add_argument('-n', '--list', action='store_true', dest='list_',
                      help='list archive contents without extracting')

  args = parser.parse_args()

  for name in args.archive:
    try:
      print 'unpacking %r:' % name
      with open(name, 'rb') as archive:
        unpack(archive, extract=not args.list_)

    except:
      sys.stderr.write(traceback.format_exc())

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if __name__ == '__main__':
  main()
