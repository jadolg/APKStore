#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from zipfile import ZipFile
from glob import glob as listDir
from os import remove, mkdir, rename
from os.path import exists, basename, dirname
from sys import argv
import os
import re
import subprocess
import sqlite3

from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APKStore.settings')


POOL = settings.APK_ROOT
OUTPUT = settings.ICONS_ROOT

DB = settings.DB_URL


def listAPKs():

    def listar(dir):
        alista = []
        alista.extend(listDir(dir+"/*.apk"))

        for i in os.listdir(dir):
            if os.path.isdir(dir+"/"+i):
                alista.extend(listar(dir+"/"+i))

        return alista

    lista = []
    for i in POOL:
        l = listar(i)
        lista.append(l)
        print len(l),"applications found on",i

    if len(lista) > 0:
        return lista
    else:
        raise Exception("No applications found")

def getRelatives(afile):
    rel = ""
    dir = os.path.dirname(afile)
    for i in os.listdir(dir):
        if os.path.isfile(dir+"/"+i) and i != basename(afile):
            rel += ":"+i
    return rel

def makeDir(afile,i):
    data = getData(afile)
    if basename(dirname(afile)) != data[0]+"_"+data[3]:
        dir = dirname(afile)+os.sep+data[0]+"_"+data[3]
        newfile = dir+os.sep+basename(afile)
        print dir,"===",newfile
        try:
            #pass
            mkdir(dir)
        except:
            print 'cant make dir',dir
        rename(afile,newfile)

def makeDirs():
    c = 0
    for i in listAPKs():
        for j in i:
            try:
                makeDir(j,c)
            except:
                print "can't process",j
        c += 1


def cleanIcons():
    for i in listDir(OUTPUT+"/*.png"):
        print 'removing ',i
        os.remove(i)

def getData(afile):
    p = subprocess.Popen(['./aapt','d','badging',afile], stdout=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise Exception(err)
    else:
        try:
            name_re = "application: label='(.*?)'"
            icon_re = "application: label='.*?' icon='(.*?)'"
            versionCode_re ="versionCode='(.*?)'"
            versionName_re ="versionName='(.*?)'"
            name = re.findall(name_re,out,re.DOTALL)
            icon = re.findall(icon_re,out,re.DOTALL)
            version = re.findall(versionCode_re,out,re.DOTALL)
            versionName = re.findall(versionName_re,out,re.DOTALL)
            name[0] = str(name[0]).replace("\n"," ")
            if name[0] == "":
                name[0] = basename(afile)
            versionName[0] = str(versionName[0]).replace("\n"," ")
            return [name[0],icon[0],versionName[0],version[0]]
        except:
            return None

def extractIcon(aapk,ind):
    try:
        afile = ZipFile(aapk)
        data = getData(aapk)
        if data:
            fin = afile.open(data[1])
            fout = open(OUTPUT+"/"+str(ind)+"_"+data[0]+".png",'w')
            fout.write(fin.read())
            fin.close()
            fout.close()
            return str(ind)+"_"+data[0]+".png"

    except:
        return "no_icon.png"

def createDB():
    database = sqlite3.connect(DB)
    cursor  = database.cursor()
    #nombre icon ruta versionName versionCode poolindex id archivosrelativos
    cursor.execute("create table apks (nombre text, icon text, ruta text, versionName text, version text,pool text,id int,relativo text)")
    ind = 0
    r = 0
    for k in listAPKs():
        for i in k:
            theAPKdata = getData(i)
            if theAPKdata:
                nombre = theAPKdata[0]
                icon = extractIcon(i,ind)

                versionName = theAPKdata[2]
                version = theAPKdata[3]

                data = (nombre,icon,i.replace(POOL[r],""),versionName,version,str(r),ind,getRelatives(i))
                ind += 1
                #print data
                try:
                    cursor.execute("insert into apks values (?,?,?,?,?,?,?,?)",data)
                except:
                    print ("Can not insert "+nombre+" file: "+i)
                database.commit()
            else:
                print ("Can not get data from file: "+i)

        r += 1

def cleanDB():
    if exists(DB):
        print 'deleting database...'
        remove(DB)

    print 'deleting icons...'
    cleanIcons()

def CleanAndBuildDB():
    cleanDB()

    print 'creating database...'
    createDB()


def main():
    if argv[1] == 'clean':
        cleanDB()
    elif argv[1] == 'build':
        CleanAndBuildDB()
    elif argv[1] == 'makedirs':
        makeDirs()
    else:
        print 'nothing to do!!'

if __name__ == '__main__':
	main()