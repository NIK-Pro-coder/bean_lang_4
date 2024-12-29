
from tokenparser import parseTokens
from termcolor import cprint
import json

def initError(string) :
	text = {x: parseTokens(x)[0] for x in string.split("\n")}
	num_dict = {x: n for n, x in enumerate(string.split("\n"))}

	def error(line: list[dict[str, str]] | int, errType: str, errMsg: str, under: list[str], err: bool = True) :

		if type(line) is list :
			ln = [x for x in text if text[x] == line][0]

			num = num_dict[ln] + 1
		elif type(line) is int :
			num = line + 1

			ln = [x for x in num_dict if num_dict[x] == line][0]
		else : return

		vals = [x["val"] for x in text[ln] if x["val"] != "\n"]

		strp = ln.strip()

		underline = ""
		for i in vals :
			bef = "~" * (len(strp) - len(strp.lstrip()))
			strp = strp.strip()

			add = ("^" if i in under else "~") * len(i)
			strp = strp.removeprefix(i)

			underline += bef + add

		for i in underline :
			underline = underline.replace("^~^", "^^^")

		mycol = "red" if err else "yellow"

		print(num, "|", end = " ")
		for n, i in enumerate(ln.strip()) :
			col = mycol if underline[n] == "^" else "white"
			cprint(i, col, end = "")
		print()
		print(" " * len(str(num)), "|", end = " ")
		cprint(underline, mycol)
		cprint(errType + " " + ("error" if err else "warning") + ": " + errMsg, mycol)
		print()

	return error
