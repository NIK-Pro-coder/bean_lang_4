
import re

token_types = {
	"comment": ["#.*"],
	"longComment": ["/\\*(.|\n)*\\*/"],

	"range": ["\\.\\."],

	"str": ["\"[^\"]*\""],
	"float": [
		" -[0-9]*\\.[0-9]+",
		"[0-9]*\\.[0-9]+"
	],
	"int": [
		" -[0-9]+",
		"[0-9]+"
	],
	"bool": [
		"true",
		"false"
	],

	"assign": [
		"\\+=",
		"-=",
		"\\*=",
		"/=",
		"\\|=",
		"%=",
		"&=",
		"=",
	],

	"return": ["->"],

	"binaryOp": [
		"&&",
		"\\|\\|",
		"\\^\\^"
	],
	"numOp": [
		"\\+",
		"\\*",
		"/",
		"-",
		"%",
		"\\^"
	],
	"strOp": ["><"],
	"boolOp": [
		"\\|",
		"&"
	],
	"logicOp": [
		">=",
		"<=",
		"==",
		"!=",
		">",
		"<"
	],

	"parenteses": [
		"\\(",
		"\\)",
		"\\[",
		"\\]",
		"\\{",
		"\\}"
	],

	"type": [
		"(\n| )int(\n| )",
		"(\n| )str(\n| )",
		"(\n| )float(\n| )",
		"(\n| )bool(\n| )",
		"(\n| )func(\n| )",
		"(\n| )void(\n| )",
		"(\n| )struct(\n| )"
	],
	"keyword": [
		"(\n| )const(\n| )",
		"(\n| )return(\n| )",
		"(\n| )fn(\n| )",
		"(\n| )for(\n| )",
		"(\n| )in(\n| )",
		"(\n| )elif(\n| )",
		"(\n| )if(\n| )",
		"(\n| )else(\n| )",
		"(\n| )while(\n| )",
		"(\n| )include(\n| )",
	],

	"argSplit": [","],

	"identifier": ["[a-z|A-Z|0-9|_]+"],

	"newline": ["\n"]
}

def parseTokens(text: str,
		debug: bool = False) -> tuple[list[dict[str,
		str]],
		dict] :
	text = text.replace("\t",
		" ")

	regex = {}

	tokens = []
	for type in token_types :
		for tkn in token_types[type] :
			for i in re.finditer(tkn,
		text) :
				add = True
				span_i = i.span()
				for t in tokens :
					span_t = t["val"].span()
					if (span_i[0] < span_t[1] and span_i[1] > span_t[0])\
					or (span_i[1] < span_t[1] and span_i[1] > span_t[1]):
						add = False
						break
				if add :
					if not type in regex :
						regex[type] = []

					regex[type].append({
						"span": i.span(),
						"match": i.group().strip() if type != "newline" else i.group(),
					})

					tokens.append({
						"val": i,
						"type": type
					})

	tokens.sort(key=lambda x: x["val"].span()[0])

	tokens = [
		{
			"val": x["val"].group(),
			"type": x["type"]
		}
		for x in tokens
	]

	new = []

	for i in tokens :
		if i["type"] == "longComment" :
			for l in range(i["val"].count("\n")) :
				new.append({"val": "\n", "type": "newline"})
			new.append(i)
		elif i["type"] != "newline" and "\n" in i["val"] :
			for l in range(len(i["val"]) - len(i["val"].lstrip("\n"))) :
				new.append({"val": "\n", "type": "newline"})
			new.append({"val": i["val"].strip("\n "), "type": i["type"]})
			for l in range(len(i["val"]) - len(i["val"].rstrip("\n"))) :
				new.append({"val": "\n", "type": "newline"})
		elif " " in i["val"] :
			new.append({"val": i["val"].strip(" "), "type": i["type"]})
		else :
			new.append(i)

	return new, regex
