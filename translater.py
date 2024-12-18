import os
import tomli
from copy import deepcopy
from termcolor import cprint
from pathlib import Path

home = Path.home()

templates = home / ".config/beanlang/templates"

secs = []
conv = {}
inde = ""

def getVal(val, f) :
	s = deepcopy(f)
	for i in val.strip("$").split(".") :
		s = s[i]

	return s

def extract(f) :
	deep = []
	depth = 0
	curr = []
	for i in f :
		if i == "$]" : depth -= 1

		if depth > 0 : curr.append(i)
		elif i != "$]" : curr = [i]
		else : curr.append(i)

		if i == "$[" : depth += 1

		if depth == 0 :
			if len(curr) > 1 :
				deep.append(extract(curr[1:-1]))
			else :
				deep.append(curr[0])
			curr = []

	return [x for x in deep if x]

def replace(deep, field, depth) :
	new = []
	for i in deep :
		if type(i) is str :
			if i.startswith("$") :
				if i.startswith("$$") :
					secs = getVal(i[2:], field)
					for s in secs :
						new.append("\n" + inde * (depth + 1) + translateSection(s, depth + 1))
				else :
					new.append(getVal(i, field))
			else :
				new.append(i)
		else :
			if "!for" in i :
				add = i[i.index("!split")+1:] if "!split" in i else []
				val = i[:i.index("!for")]
				base = getVal(i[i.index("!in") + 1], field)
				name = i[i.index("!for") + 1]

				for n,b in enumerate(base) :
					new.extend(replace(val, {name: b}, depth))
					if n < len(base) - 1 and add :
						new.extend(add)
			else :
				cond = i[i.index("!if")+1]
				val = i[:i.index("!if")]

				if getVal(cond, field) :
					new.extend(replace(val, field, depth))

	return new

def translateSection(s, depth = 0) :
	if not s["type"] in secs :
		cprint(f"Translation string for section type \"{s["type"]}\" is not defined!", "red")
		exit(1)

	tem: list[str] = secs[s["type"]].replace("\\", " \\ ").replace("\n", " \n \\ ").split(" ")
	deep = extract(tem)
	new = replace(deep, s["fields"], depth)

	for n,i in enumerate(new) :
		if i in conv :
			new[n] = conv[i]

	stg = []

	for i in new :
		if i == "\\" :
			if stg[-1] == " " :
				stg.pop(-1)
		else :
			stg.append(i.strip(" "))
			stg.append(" ")

	return "".join(stg).replace(" \n", "\n")

def getNum(min: int, max: int, msg: str) -> int :
	ini = input(msg)

	if ini.isdecimal() :
		t = int(ini)
		if t >= min and t < max :
			return t
		else :
			return getNum(min, max, "Enter a valid number ")
	else :
		return getNum(min, max, "Enter a valid number ")

def translate(filename: str, sections: list[dict], lang: str) :
	global secs, conv, inde

	print("Loading language templates")
	langs = [
		x
		for x in os.listdir(templates)
		if os.path.isfile(templates / x)
	]

	possible = []

	for i in langs :
		with open(templates / i) as f :
			mine = tomli.loads(f.read())
			match mine["meta"] :
				case {
					"version": str(),
					"author": str(),
					"description": str()
				} :
					...
				case _ :
					cprint(f"'{i}' has a malformed meta header, you might want to check that", "red")
					cprint("  Expected: version, author, description", "red")
					cprint("  Found:    " + ", ".join(mine["meta"].keys()), "red")
					continue

			match mine["lang"] :
				case {
					"name": str(),
					"extension": str(),
					"indentation": str()
				} :
					...
				case _ :
					cprint(f"'{i}' has a malformed lang header, you might want to check that", "red")
					cprint("  Expected: name, extension, indentation", "red")
					cprint("  Found:    " + ", ".join(mine["lang"].keys()), "red")
					continue

		if lang == mine["lang"]["name"] or lang == mine["lang"]["extension"] :
			possible.append((deepcopy(mine), i))

	template = {}
	fname = ""

	if len(possible) >= 1 :
		lang = possible[0][0]["lang"]["name"]
		if len(possible) > 1 :
			print()

			for n,i in enumerate(possible) :
				print(f"{n}. '{i[1]}' by {i[0]["meta"]["author"]} (version {i[0]["meta"]["version"]})")
			print(f"Found {len(possible)} templates for {lang}, which one to use?", end = " ")
			num = getNum(0, len(possible), "")

			template = deepcopy(possible[num][0])
			fname = possible[num][1]
		else :
			template = deepcopy(possible[0][0])
			fname = possible[0][1]
	elif len(possible) == 0 :
		cprint(f"Could not load template for language: {lang}", "red")
		exit(1)

	cprint(f"Loaded template '{fname}' (version {template["meta"]["version"]}) by {template["meta"]["author"]}", "green")

	secs = template["sections"]
	conv = template["conversions"] if "conversions" in template else []
	inde = template["lang"]["indentation"]

	last_type = ""

	full = " " + secs["headers"] if "headers" in secs else ""

	for s in sections :
		string = translateSection(s)

		if s["type"] != last_type :
			last_type = s["type"]
			full += "\n"

		full += "\n" + string.rstrip("\t ")

	newname = filename[:filename.rfind(".")+1] + template["lang"]["extension"]

	with open(newname, "w") as f :
		f.write(full[1:])
	cprint("File successfully translated", "green")
