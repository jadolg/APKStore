#!/bin/bash
echo "copiando archivos"
cp tmp/APKStore/Install/apkstore /etc/init.d/
chmod +x /etc/init.d/apkstore

cp tmp/APKStore/Install/apkstore.conf /etc/

cp tmp/APKStore/Install/apkstore_server /usr/sbin/
cp tmp/APKStore/Install/filldb /usr/sbin/

chmod +x /usr/sbin/apkstore_server
chmod +x /usr/sbin/filldb

cp -R tmp/APKStore /opt/

echo "iniciando servicio"
service apkstore start
echo "instalación finalizada"
