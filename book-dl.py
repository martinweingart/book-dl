#!/home/mweingart/Proyectos/scripts/book-dl/bin/python
# -*- coding: utf-8 -*-

import argparse
import foxebooks
import epublibre

parser = argparse.ArgumentParser();
parser.add_argument("url", help="Url de descarga")
parser.add_argument("-a", "--all", action="store_true", help="Descargar todas las páginas")
parser.add_argument("-d", "--dest", help="Carpeta destino")
parser.add_argument("-b", "--byear", help="No se descargan libros con año de publicación menores a este valor")
parser.add_argument("-i", "--inicio", help="Si es una lista de libros, el índice de inicio de descarga")
parser.add_argument("-j", "--fin", help="Si es una lista de libros, el índice de fin de descarga")
parser.add_argument("-e", "--editorial", help="Descargar los libros de una editorial seleccionada")
parser.add_argument("--editorials", action="store_true",
                    help="Lista las editoriales disponibles para descargar")
parser.add_argument("-p", "--pages", help="Cantidad de páginas a analizar")
parser.add_argument("-r", "--repeated", help="Descargar nuevamente si ya existen")
args = parser.parse_args()

editoriales_foxebook = {
    'oreilly-media': 'http://www.foxebook.net/publisher/oreilly-media/?sort=daterank',
    'apress': 'http://www.foxebook.net/publisher/apress/?sort=daterank',
    'packtpub': 'http://www.foxebook.net/publisher/packtpub/?sort=daterank',
    'addison-wesley-professional': 'http://www.foxebook.net/publisher/addison-wesley-professional/?sort=daterank',
    'manning-publications': 'http://www.foxebook.net/publisher/manning-publications/?sort=daterank',
    'no-starch-press': 'http://www.foxebook.net/publisher/no-starch-press/?sort=daterank',
    'springer': 'http://www.foxebook.net/publisher/springer/?sort=daterank',
    'princeton-university-press': 'http://www.foxebook.net/publisher/princeton-university-press/?sort=daterank',
    'chapman-and-hallcrc': 'http://www.foxebook.net/publisher/chapman-and-hallcrc/?sort=daterank',
    'wiley-ieee-press': 'http://www.foxebook.net/publisher/wiley-ieee-press/?sort=daterank'
}

def main():
    if 'foxebook' in args.url:
        if args.editorials:
            for e in editoriales_foxebook.keys():
                print e
        url = editoriales_foxebook[args.editorial] if editoriales_foxebook[args.editorial] else args.url
        foxebooks.main(url, args.dest, args.byear, args.all, args.pages, args.repeated)
    elif 'epublibre' in args.url:
        epublibre.main(args.url, args.inicio, args.fin)


if __name__ == "__main__":
    main()
