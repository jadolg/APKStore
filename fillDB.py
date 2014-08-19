#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  fillDB.py
#
#  Copyright 2014 Jorge Alberto Díaz Orozco <jaorozco@estudiantes.uci.cu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.


from zipfile import ZipFile
from glob import glob as listDir
from os import mkdir, rename, chmod
from os.path import basename, dirname
from sys import argv,stdout
import os
import re
import subprocess
from hashlib import sha256




from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APKStore.settings')

from APKIndex.models import apks

POOL = settings.APK_ROOT
OUTPUT = settings.ICONS_ROOT
PATH = settings.BASE_DIR

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
            mkdir(dir)
            chmod(dir,0777)
        except:
            print 'cant make dir',dir
        rename(afile,newfile)
        chmod(newfile,0777)

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
        if i != OUTPUT+"/no_icon.png":
            print 'removing ',i
            os.remove(i)

def getData(afile):
    if (os.path.exists(PATH+'/aapt')):
        print 'here'
        p = subprocess.Popen([PATH+'/aapt','d','badging',afile], stdout=subprocess.PIPE)
    else:
        p = subprocess.Popen(['/opt/APKStore/aapt','d','badging',afile], stdout=subprocess.PIPE)
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
    ind = 0
    r = 0
    amm = 0
    lapk = listAPKs()
    for k in lapk:
        amm += len(k)

    for k in lapk:
        for i in k:
            theAPKdata = getData(i)
            if theAPKdata:
                nombre = theAPKdata[0][:30]
                icon = extractIcon(i,ind)

                versionName = theAPKdata[2][:20]
                version = theAPKdata[3]

                ind += 1
                data = open(i,"rb").read(512)
                thash = sha256(data)
                sha =  thash.hexdigest()

                try:
                    aux = apks.objects.filter(sha=sha)
                    if len(aux) > 0:
                        print 'aplicacion duplicada',i
                    else:
                        a = apks(sha=sha,nombre=nombre,icon=icon,descripcion="",ruta=i.replace(POOL[r],""),versionName=versionName,version=version,pool=str(r),ind=ind,relativo=getRelatives(i))
                        a.save()
                except:
                    print ("Can not insert "+nombre+" file: "+i)

            else:
                print ("Can not get data from file: "+i)
            print ">> "+str(ind)+'/'+str(amm)
        r += 1

def cleanDB():
    print 'cleaning database...'
    apks.objects.all().delete()

    print 'deleting icons...'
    cleanIcons()

def CleanAndBuildDB():
    cleanDB()

    print 'creating database...'
    createDB()


def main():
    if len(argv)>1:
        if argv[1] == 'clean':
            cleanDB()
        elif argv[1] == 'build':
            CleanAndBuildDB()
        elif argv[1] == 'makedirs':
            makeDirs()
        else:
            print 'nothing to do!!'
    else:
        print "use: filldb clean|build|makedirs"

if __name__ == '__main__':
	main()
