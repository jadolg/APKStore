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
from os.path import basename, dirname, exists
from sys import argv
import os
import re
import subprocess
from hashlib import sha256
from shutil import move
from os import remove

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APKStore.settings')

from APKIndex.models import apks

POOL = settings.APK_ROOT
OUTPUT = settings.ICONS_ROOT
PATH = settings.BASE_DIR


def list_apks():
    def listar(dir):
        alista = []
        alista.extend(listDir(dir + "/*.apk"))

        for i in os.listdir(dir):
            if os.path.isdir(dir + "/" + i):
                alista.extend(listar(dir + "/" + i))

        return alista

    lista = []
    for i in POOL:
        l = listar(i)
        lista.append(l)
        print len(l), "applications found on", i

    if len(lista) > 0:
        return lista
    else:
        raise Exception("No applications found")


def get_relatives(afile):
    rel = ""
    dir = os.path.dirname(afile)
    for i in os.listdir(dir):
        if os.path.isfile(dir + "/" + i) and i != basename(afile):
            rel += ":" + i
    return rel


def make_dir(afile):
    data = get_data(afile)
    if data == None:
        move(afile, settings.TRASHCAN)
        return

    if basename(dirname(afile)) != data[0] + "_" + data[3]:
        adir = dirname(afile) + os.sep + data[0] + "_" + data[3]
        newfile = adir + os.sep + basename(afile)
        print adir, "===", newfile
        try:
            mkdir(adir)
            chmod(adir, 0777)
        except:
            print 'cant make dir', adir
        rename(afile, newfile)
        chmod(newfile, 0777)


def make_dirs():
    for i in list_apks():
        for j in i:
            try:
                make_dir(j)
            except:
                print "can't process", j


def clean_icons():
    for i in listDir(OUTPUT + "/*.png"):
        if i != OUTPUT + "/no_icon.png":
            print 'removing ', i
            os.remove(i)


def get_data(afile):
    if (os.path.exists(PATH + '/aapt')):
        p = subprocess.Popen([PATH + '/aapt', 'd', 'badging', afile], stdout=subprocess.PIPE)
    else:
        p = subprocess.Popen(['/opt/APKStore/aapt', 'd', 'badging', afile], stdout=subprocess.PIPE)
    out, err = p.communicate()
    if err:
        raise Exception(err)
    else:
        try:
            name_re = "application: label='(.*?)'"
            icon_re = "application: label='.*?' icon='(.*?)'"
            versionCode_re = "versionCode='(.*?)'"
            versionName_re = "versionName='(.*?)'"
            name = re.findall(name_re, out, re.DOTALL)
            icon = re.findall(icon_re, out, re.DOTALL)
            version = re.findall(versionCode_re, out, re.DOTALL)
            versionName = re.findall(versionName_re, out, re.DOTALL)
            name[0] = str(name[0]).replace("\n", " ")
            if name[0] == "":
                name[0] = basename(afile)
            versionName[0] = str(versionName[0]).replace("\n", " ")
            return [name[0], icon[0], versionName[0], version[0]]
        except:
            return None


def extract_icon(aapk, ind):
    try:
        afile = ZipFile(aapk)
        data = get_data(aapk)
        if data:
            fin = afile.open(data[1])
            fout = open(OUTPUT + "/" + str(ind) + "_" + data[0] + ".png", 'w')
            fout.write(fin.read())
            fin.close()
            fout.close()
            return str(ind) + "_" + data[0] + ".png"

    except:
        return "no_icon.png"


def create_db():
    ind = 0
    repo_index = 0
    amm = 0
    lapk = list_apks()
    #calcular la cantidad total de aplicaciones
    for k in lapk:
        amm += len(k)

    for k in lapk:
        for i in k:
            theAPKdata = get_data(i)
            if theAPKdata:
                ruta = i.replace(POOL[repo_index], "")

                mkl = apks.objects.filter(ruta=ruta)
                if len(mkl):
                    continue

                nombre = theAPKdata[0][:30]
                icon = extract_icon(i, ind)

                versionName = theAPKdata[2][:20]
                version = theAPKdata[3]

                ind += 1
                data = open(i, "rb").read()
                thash = sha256(data)
                sha = thash.hexdigest()

                try:
                    aux = apks.objects.filter(sha=sha)
                    if len(aux) > 0:
                        move_or_delete(i)
                        print 'aplicacion duplicada', i, 'movida a', settings.TRASHCAN
                    else:
                        a = apks(sha=sha, nombre=nombre, icon=icon, descripcion="", ruta=i.replace(POOL[repo_index], ""),
                                 versionName=versionName, version=version, pool=str(repo_index), ind=ind,
                                 relativo=get_relatives(i))
                        a.save()
                except:
                    move_or_delete(i)
                    print "No se puede insertar " + nombre + " archivo: " + i + ' movida a ' + settings.TRASHCAN

            else:
                print "No se puede obtener los datos de: " + i + ' movida a ' + settings.TRASHCAN
                move_or_delete(i)

            print ">> " + str(ind) + '/' + str(amm)
        repo_index += 1

def move_or_delete(i):
    try:
        print 'moviendo '+i+' a '+settings.TRASHCAN
        move(i, settings.TRASHCAN)
    except:
        print 'error moviendo. intentando eliminar'
        try:
            remove(i)
        except:
            print 'error eliminando. revise los permisos sobre este archivo.'


def clean_db():
    print 'cleaning database...'
    apks.objects.all().delete()

    print 'deleting icons...'
    clean_icons()


def clean_and_build_db():
    clean_db()

    print 'creating database...'
    create_db()


def update():
    #limpiar la base de datos de registros inexistentes
    for apk in apks.objects.all():
        if not exists(settings.APK_ROOT[int(apk.pool)] + apk.ruta):
            print 'removing non existing apk for:', apk.nombre
            apk.delete()

    #Reindizar las aplicaciones
    create_db()


def main():
    if len(argv) > 1:
        if argv[1] == 'clean':
            clean_db()
        elif argv[1] == 'build':
            clean_and_build_db()
        elif argv[1] == 'makedirs':
            make_dirs()
        elif argv[1] == 'update':
            update()
        else:
            print 'nothing to do!!'
    else:
        print "use: filldb clean|build|update|makedirs"


if __name__ == '__main__':
    main()
