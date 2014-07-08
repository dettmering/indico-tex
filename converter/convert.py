#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import codecs
import hashlib
import xml.etree.ElementTree as ET

datasource = sys.argv[1]

tree = ET.parse(datasource)
abstr = tree.getroot()

def hash(str):
	sha1 = hashlib.sha1()
	sha1.update(str)
	return sha1.hexdigest()

def getAuthors(id):
	authors = []

	for x in abstr[id]:
		if x.tag == "PrimaryAuthor" or x.tag == "Co-Author":
			authors_temp = []
			for y in x:
				authors_temp.append(y.text)
			authors.append(authors_temp)
		
	return authors

# Escapes TeX characters and generates correct typography.

def escapeTex(str):
	str = str.replace("#", "\#")
	str = str.replace("&", "\&")
	str = str.replace("%", "\%")
	str = str.replace("~", "\~")
	
	# Correct scientific notation
	
	str = str.replace("\n", "\n\n") # Make paragraph out of new line as intended
	str = str.replace("  ", " ") # Replace double-space
	str = str.replace("in vivo", "\\emph{in vivo}")
	str = str.replace("ex vivo", "\\emph{ex vivo}")
	str = str.replace("in-vivo", "\\emph{in vivo}")
	str = str.replace("ex-vivo", "\\emph{ex vivo}")
	str = str.replace("in vitro", "\\emph{in vitro}")
	str = str.replace("in-vitro", "\\emph{in vitro}")
	str = str.replace("In vivo", "\\emph{In vivo}")
	str = str.replace("Ex vivo", "\\emph{Ex vivo}")
	str = str.replace("In-vivo", "\\emph{In vivo}")
	str = str.replace("Ex-vivo", "\\emph{Ex vivo}")
	str = str.replace("In vitro", "\\emph{In vitro}")
	str = str.replace("In-vitro", "\\emph{In vitro}")
	str = str.replace("et al", "\\emph{et~al}")
#	str = str.replace(" +/-", "±".decode("utf-8"))
	str = str.replace("+/- ", "+/– ".decode("utf-8"))
	str = str.replace("+/+", "\\textsuperscript{+/+}")
	str = str.replace("-/-", "\\textsuperscript{–/–}".decode("utf-8"))
	
	str = str.replace(" Gy", "~Gy")
	str = str.replace(" h ", "~h ") # trailing space to circumvent change of whole words
	str = str.replace(" d ", "~d ") # trailing space to circumvent change of whole words
	str = str.replace(" days", "~days")
	str = str.replace(" hrs", "~hrs")
	str = str.replace(" min ", "~min ")
	str = str.replace("mm3", "mm\\textsuperscript{3}")
	str = str.replace("cm2", "cm\\textsuperscript{2}")
	str = str.replace("Ca2+", "Ca\\textsuperscript{2+}")
	str = str.replace("K+", "K\\textsuperscript{+}")
	str = str.replace("Cl-", "Cl\\textsuperscript{–}".decode("utf-8"))
	str = str.replace("60Co", "\\textsuperscript{60}Co")
	str = str.replace("12C", "\\textsuperscript{12}C")
	str = str.replace("Cs137", "\\textsuperscript{137}Cs")
	str = str.replace("Cs-137", "\\textsuperscript{137}Cs")
	str = str.replace("CO2", "CO\\textsubscript{2}")
	str = str.replace(" O2", " O\\textsubscript{2}")
	str = str.replace("H2O2", "H\\textsubscript{2}O\\textsubscript{2}")

	return str

# Used for finding common affiliations

def findUnique(set):
	output = []
	for x in set:
		if x not in output:
			output.append(x)
	return output

# Reads abstract by ID

def getAbstract(id):
	abs_id = abstr[id][0].text
	title = abstr[id][1].text
	content = abstr[id][2].text
	authors = getAuthors(id)
	
	return abs_id, title, authors, content

# Generates LaTeX output

def texOutput(data):
	output = []
	
	abs_id = data[0] + "\n"
	title = data[1] + "\n"
	content = data[3]

	# Generate authors and affiliations

	authors = ""

	nComma = len(data[2]) - 1
	iComma = 0

	affiliations = []
	
	for w in data[2]:
		aff = w[3].encode("utf-8")
		affiliations.append(aff)

	nUnique = len(findUnique(affiliations))
	toc_authors = []

	for x in data[2]:
		aff = x[3]
		authors += x[0][0] + ". " + x[1]
		toc_authors.append(x[1])
#		if (nUnique > 1):
#			Funktion die index fuer Autoren ausgibt
		if (iComma < nComma):
			authors += ", "
		iComma += 1

	authors += "\n"
	
	# Unique affiliations are replaced by a SHA1 hash to assign the correct index for each author.
	# A TeX counter is initialized for each abstract which counts the unique affiliations
	
	affil = ""
	
	affilidx = 1
	
	for y in findUnique(affiliations):
		affil += str(affilidx) + " " + y + "\n"
		affilidx += 1
	
	affil += "\n"
	

	# Building the file

	output.append(abs_id.encode("utf-8"))
	output.append(title.encode("utf-8"))
	output.append(authors.encode("utf-8"))
	output.append(affil)
	output.append(content.encode("utf-8"))
	
	return output

def writeFile(filename, data):
	fo = open(filename, "wb+")
	print filename
	for x in data:
		fo.write(x)
		fo.write("\n")
	fo.close()

# Execution

nAbstracts = len(abstr) - 1
id = 1
fileList = []

# Iterate through all abstracts and generate a .tex file for each abstracts
# Generate a list of abstracts.

while (id <= nAbstracts):
	a = getAbstract(id)
	
	filename = a[0]
	
	writeFile(filename+".tex", texOutput(a))
	fileList.append("\\input{"+filename+"} \\newpage")
	id += 1
	
writeFile("abstractlist.tex", fileList)