#!/usr/bin/python2
# Requirements:
#  * bibtexparser
#  * urllib2

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *
import bibtexparser
import io
import argparse
import urllib2
import re


def monthNameToNumber( monthName ):
    monthNames = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]
    if monthNames.count( monthName ):
        return str(monthNames.index( monthName ) + 1).zfill(2)
    else:
        return monthName

def downloadToFile( tmpFileName, urlList ):
    with open(tmpFileName, "w") as f:
        for url in urlList:
            response = urllib2.urlopen( url )
            f.write( response.read() )
    f.close()
    return tmpFileName

def getNumberOfRecords(url):
    lines = urllib2.urlopen( url ).readlines()
    for line in lines:
        if "CMS Papers : " in line:
            m = re.search('.*<strong>(\d+)</strong> records.*', line)
            if m:
                x = int(m.group(1))
                print "Found", x, "records."
                return x
    print "Did not find any records"
    return 0



def prettifyTitle( title ):
    replacements = [
            ("\n"," "),
            ("\bar", "&oline;"),
            ("\rightarrow", "&rarr;" ),
            ("gamma", "&gamma;"),
            ("\\",""),
            ("{",""),
            ("}",""),
            ("mathrm", ""),
            ( "sqrt", "&radic;" ),
            ( "TeV", "!TeV" ),
            ( "GeV", "!GeV" ),
            ("$",""),
            ("|",""),
            ]
    for old, new in replacements:
        title = title.replace( old, new )
    title = " ".join(title.split())
    return title

def printTwikiLine( title, year, month, link, referenz ):
    '''Formating the text and create one line per entry.'''

    title = prettifyTitle( title )
    date = '%s.%s'%( monthNameToNumber( month ), year )
    twikiLink = '[[%s][%s]]'%(link, referenz) if link else referenz
    sign = ' ' if link else 'x'

    return "| |%s| %s | %s | %s | |"%( sign, title, date, twikiLink )

def createTwikiText(fileName):
    '''Here the downloaded html file is opended, and the bibtex part is interpreted.
    Articles are published, technical reports not, and have to be treated spearately.'''

    twikiText = ""
    with open(fileName) as bibfile:
        bp = bibtexparser.load(bibfile)
        for entry in bp.get_entry_list():
            if entry["ID"] == "Chatrchyan:1129810": continue # CMS experiment. Has no month
            if entry["ENTRYTYPE"] not in ["techreport", "article"]: continue
            title = entry["title"]
            year = entry["year"]
            month = entry["month"]
            if entry["ENTRYTYPE"] == "article":
                print entry['number']
                link = "http://arxiv.org/abs/%s"%entry['number'].split()[0][6:-1]
                print link
                if "volume" not in entry: continue
                referenz = "%s %s(%s) %s"%(entry['journal'], entry['volume'], entry['year'], entry['pages'].split(".")[0] )
            else:
                link = ""
                referenz = "Not published"
            twikiText += printTwikiLine(title, year, month, link, referenz) + "\n"

    with io.open("literaturseminarOutput.txt", "w", encoding="utf8") as f:
        f.write(twikiText)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--noUpdate", action="store_true")
    parser.add_argument("--tmpFileName", default="tmpBibFile.html")
    args = parser.parse_args()

    if not args.noUpdate:
        nRec = getNumberOfRecords("http://cds.cern.ch/search?cc=CMS+Papers&rg=1")
        downloadToFile(args.tmpFileName, ["http://cds.cern.ch/search?cc=CMS+Papers&so=a&of=hx&rg=200&jrec=%s"%(1+200*i) for i in range(nRec/200+1)])
    twikiText = createTwikiText(args.tmpFileName)



