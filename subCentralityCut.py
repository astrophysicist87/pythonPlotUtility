#!/usr/bin/env python

from sys import argv, exit
import sys
sys.path.insert(0, '/Users/Chun/Documents/pythonPlotUtilities')

from os import path, remove
from DBR import SqliteDB
from numpy import *

try:
   fromDBName = str(argv[1])
   toDBName = str(argv[2])
   totalCent = str(argv[3]).split('-')
   subcutCent = str(argv[4]).split('-')
except:
   print("Usage: subCentrlityCut.py totalDatabaseName subcutDataabaseName Centrality_of_totalDatabase Centrality_of_subcutDatabase")
   exit()

fromDB = SqliteDB(path.abspath(fromDBName))

if path.exists(path.abspath(toDBName)):
    remove(path.abspath(toDBName))

toDB = SqliteDB(path.abspath(toDBName))

nevent = len(fromDB._executeSQL("select event_id from multiplicities where pid = 1001").fetchall())
nsample = int(nevent*(float(subcutCent[1]) - float(subcutCent[0]))/(float(totalCent[1]) - float(totalCent[0])))
noffset = int(nevent*(float(subcutCent[0]) - float(totalCent[0]))/(float(totalCent[1])- float(totalCent[0])))

if noffset > nevent or noffset < 0:
    sys.stderr.write('offset is out of boundary!\n')
    exit()
if nsample + noffset > nevent or nsample < 0:
    sys.stderr.write('centrality cut is out of boundary!\n')
    exit()

for aTable in fromDB.getAllTableNames():
    print(aTable)
    # first copy table structure
    firstCreation = toDB.createTableIfNotExists(aTable, fromDB.getTableInfo(aTable))
    if "lookup" in aTable: # just copy
        toDB.insertIntoTable(aTable, fromDB.selectFromTable(aTable))
    elif "multiplicities" in aTable:
        toDB.insertIntoTable(aTable, fromDB._executeSQL("select * from multiplicities where pid = 1001 order by -N limit %d offset %d" % (nsample, noffset,)).fetchall())
    else:
        toDB.insertIntoTable(aTable, fromDB._executeSQL("select * from %s where event_id in (select event_id from multiplicities where pid = 1001 order by -multiplicities.N limit %d offset %d)" % (aTable, nsample, noffset,)).fetchall())
toDB.closeConnection() # commit
