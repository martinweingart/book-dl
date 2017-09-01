#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import sys
import urllib2
import re
from os import path
import getpass

def existeArchivo(file):
    filename_complete, file_extension = path.splitext(file)
    filename = filename_complete.split('/')[-1]

    downloaded_file = open(path.join('/home', getpass.getuser(), '.book-dl/foxebook'), 'r')
    downloaded_list = downloaded_file.readlines()
    for book in downloaded_list:
        if (book.strip() == filename):
            return True

    return (path.isfile(filename_complete + '.pdf') \
     or path.isfile(filename_complete + '.epub') \
     or path.isfile(filename_complete + '.azw3') \
     or path.isfile(filename_complete + '.mobi')
     or path.isfile(filename_complete + '.rar'))

#Código para descargar archivo con barra de progreso
def download(url, dest, repeated):
    if repeated or not existeArchivo(dest):
        u = urllib2.urlopen(url)
        f = open(dest, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Descargando archivo: %s Bytes: %s" % (dest, file_size)
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,
        print "\n"
        downloaded_file = open(path.join('/home', getpass.getuser(), '.book-dl/foxebook'), 'w')
        ext = dest.rfind('.')
        downloaded_file.write(dest[0:ext]+"\n")
        f.close()
        return True
    else:
        print 'El libro ya fue descargado anteriormente'
        return True


def getLinksPages(url):
    links = []
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        ultima = soup.find('a', {'title': 'Last'})
        if ultima is None:
            ultima = 0
        else:
            ultima = int(ultima.get('href').split('/')[-2])
        for i in range(0, ultima + 1):
            links.append(url + 'page/' + str(i) + '/')
    return links

def getLinksLibros(url, byear):
    links = []
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        div_books = soup.find_all('div', {'class': 'col-md-9'})
        for div in div_books:
            info = div.find_all('div', {'class': 'info'})
            date = info[2].find('i').get_text(strip=True).split(',')[1].strip()
            year = date.split('-')[0]
            if (byear is None) or (int(year) >= int(byear)):
                l = info[3].find('a', {'class': 'btn-info'})
                links.append('http://www.foxebook.net' + l.get('href'))
    return links

def getDownloadLinks(url):
    print url
    links = []
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        hrefs = soup.find('div', {'id': 'download'}).find('tbody') \
                    .find_all('a', {'target': '_blank', 'rel': 'nofollow'})
        for l in hrefs:
            href = l.get('href')
            if 'zippyshare.com' in href:
                links.append('http' + href.split('http')[-1])
    return links

def eliminarEspacioComilla(text):
    return re.sub('\s|\"', '', text)

def getDownloadUrl(url):
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        for script in soup.find_all('script'):
            if 'dlbutton' in script.text:
                m = re.search('href =(.+);', script.text)
                partes = m.group(1).split('+');
                nums1 = re.findall('\d+', partes[1])
                nums2 = re.findall('\d+', partes[2])
                num = int(nums1[0]) % int(nums1[1]) + int(nums2[0]) % int(nums2[1])
                return "/".join(url.split('/')[0:-3]) + \
                        eliminarEspacioComilla(partes[0])  + \
                        str(num) + \
                        eliminarEspacioComilla(partes[3])
    return False

def downloadBook(url, dest, repeated):
    links = getDownloadLinks(url)
    for link in links:
        down_url = getDownloadUrl(link)
        if down_url:
            return download(down_url, dest + down_url.split('/')[-1], repeated)
    return False

def main(url, dest, byear, all, pages_to_analize, repeated):
    single = True
    libros = []
    dest = dest if dest else './'

    if dest[len(dest)-1] != '/':
        dest = dest + '/'

    if not 'http://' in url:
        url = 'http://' + url

    if url == 'http://www.foxebook.net' or url == 'http://www.foxebook.net/':
        print 'La url especificada es genérica. Por favor, especificar parámetros en la url:'
        print 'Categorías, autores, publicadores, etc.'
        return

    if 'authors' in url or 'publisher' in url \
        or 'tag' in url or 'category' in url or 'search' in url:
        single = False

    if single:
        if not downloadBook(url, dest, repeated):
            print 'No se encontró ningún enlace de descarga posible'
    else:
        print "Buscando libros..."
        if all:
            url = re.sub('/page/?.*/?', '', url)

            query = ''
            if '?' in url:
                m = re.search('\?.+', url)
                query = m.group(0)
                url = re.sub('\?.+', '', url)

            link_pages = getLinksPages(url)
            total_pages = len(link_pages)
            page = 1
            print pages_to_analize
            if pages_to_analize is None:
                pages_to_analize = total_pages
            else:
                pages_to_analize = int(pages_to_analize)
            for link in link_pages[0:pages_to_analize]:
                print "Analizando página {} de {}".format(page, pages_to_analize)
                link = link + query
                libros = libros + getLinksLibros(link, byear)
                page = page + 1
        else:
            libros = getLinksLibros(url, byear)

        total_libros = len(libros)
        print "Inicio descarga de {} libros".format(total_libros)
        num_libro = 1
        for libro in libros:
            print "Descargando libro {} de {}".format(num_libro, total_libros)
            downloadBook(libro, dest, repeated)
            num_libro = num_libro + 1


if __name__ == "__main__":
    main()
