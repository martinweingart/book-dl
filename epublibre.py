#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import sys
import urllib2
import re
from os import path
import transmissionrpc
import time
import getpass

def getTorrent(url):
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        torrent = soup.find('a', {'id': 'en_desc'})
        return torrent.get('href')

def getLinksLibros(url):
    links = []
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        all_links = soup.find_all('a')
        for l in all_links:
            href = l.get('href')
            if ('/libro/' in href):
                links.append(href)
    return links

def downloadLibro(client, url):
    magnet_link = getTorrent(url)
    downloaded_file = open(path.join('/home', getpass.getuser(), '.book-dl/epublibre'), 'r+')
    downloaded_list = downloaded_file.readlines()
    for book in downloaded_list:
        if (book.strip() == url):
            print "Libro ya descargado"
            return False
    downloaded_file.write(url+"\n")
    client.add_torrent(magnet_link)

def main(url, inicio, fin):
    trans_client = transmissionrpc.Client('localhost', port=9091, user="transmission", password="transmission")

    if '/autor/' in url or '/premio/' in url or '/coleccion/' in url:
        single = False
    elif '/libro/' in url:
        single = True
    else:
        print 'Debe ingresar una url correcta'

    if single:
        downloadLibro(trans_client, url)
    else:
        libros = getLinksLibros(url)
        total_libros = len(libros)

        if total_libros == 0:
            print 'No se pudieron obtener los libros. Intente más tarde.'
            return

        print 'Libros encontrados: {}'.format(total_libros)
        i = 1
        inicio = int(inicio) if inicio else 0
        fin = int(fin) if fin else len(libros)-1
        total_libros = fin - inicio
        for libro in libros[inicio:fin]:
            if i % 5 == 0:
                time.sleep(120)
            print 'Agregando torrent {} de {}'.format(i, total_libros)
            downloadLibro(trans_client, libro)
            i  = i + 1


if __name__ == "__main__":
    main()
