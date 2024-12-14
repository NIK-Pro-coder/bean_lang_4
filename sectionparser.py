
from tokenparser import parseTokens
from typing import Callable

precedence = {
	"constDeclare": 0,
	"funcDefine": 1
}

line = 0
def parseSections(tokens: list[dict[str, str]], err: Callable | None = None) -> list[dict[str, dict]] :
	tokens.append({
		"val": "EOF",
		"type": "EOF"
	})
	sections = []
	grab = (x for x in tokens if not("comment" in x["type"].lower()))

	def getNext() :
		global line

		try :
			tkn = next(grab)
		except StopIteration :
			return {"val": "EOF", "type": "EOF"}
		if tkn["val"] == "\n" :
			line += 1
		return tkn

	tkn = getNext()

	def expect(token_type: str) -> dict[str, str] | None :
		tkn = getNext()

		if tkn["type"] == token_type\
		or (token_type.startswith("!") and tkn["val"] == token_type[1:]) :
			return tkn

		if err :
			add = "\"" if token_type.startswith("!") else ""
			err(line, "UnexpectedToken", f"Expected {add}{token_type.removeprefix("!")}{add}, instead found {tkn["val"]}", [tkn["val"]])

	def until(token_type: str) -> list[dict[str, str]] | None :
		tkns = []
		start = [line].copy()[0]
		tkn = getNext()


		while not(tkn["type"] == token_type\
		or (token_type.startswith("!") and tkn["val"] == token_type[1:])) :
			tkns.append(tkn)
			tkn = getNext()
			if err and tkn["val"] == "EOF":
				err(start, "MissingToken", f"Could not find token \"{token_type.removeprefix("!")}\"", [])
				return None

		return tkns

	def codeblock() -> tuple[list[dict[str, dict[str, str]]], dict[str, str]] :
		depth = 1
		block = []
		tkn = getNext()
		while depth > 0 :
			if tkn["val"] == "}" : depth -= 1
			if tkn["val"] == "{" : depth += 1
			if depth > 0 :
				block.append(tkn)
			tkn = getNext()

		return parseSections(block), tkn

	while tkn["type"] != "EOF" :

		tkn_type = tkn["type"]
		tkn_val = tkn["val"]

		if tkn_type == "type" :
			ntk = getNext()
			const = False
			if ntk["type"] == "identifier" :
				name = ntk
			elif ntk["val"] == "const" :
				const = True
				name = expect("identifier")
				if not name : exit(1)
			else :
				if err :
					err(line, "UnexpectedToken", f"Expected identifier or \"const\", instead found \"{ntk["val"]}\"", [ntk["val"]])
				exit(1)
			nx = getNext()
			val = []
			if nx["val"] == "=" :
				val = until("newline")

			if const :
				sections.append({
					"type": "constDeclare",
					"fields": {
						"type": tkn["val"],
						"name": name["val"],
						"val": val
					}
				})
			else :
				sections.append({
					"type": "varDeclare",
					"fields": {
						"type": tkn["val"],
						"name": name["val"],
						"val": val
					}
				})
		elif tkn_val == "if" :
			cond = until("!{")
			if not cond : exit(1)
			res, ntk = codeblock()

			elf = []

			while ntk["val"] == "elif" :
				elif_cond = until("!{")
				if not elif_cond : exit(1)
				elif_res, ntk = codeblock()
				elf.append({
					"cond": elif_cond,
					"res": elif_res
				})

			if not expect("!{") : exit(1)

			el = []
			if ntk["val"] == "else" :
				el, _ = codeblock()

			sections.append({
				"type": "ifStatement",
				"fields": {
					"cond": cond,
					"res": res,
					"elif": elf,
					"else": el
				}
			})
		elif tkn_type == "identifier" :
			ntk = getNext()
			if ntk["type"] == "assign" :
				action = ntk
				val = until("newline")
				sections.append({
					"type": "varUpdate",
					"fields": {
						"name": tkn["val"],
						"act": action["val"],
						"val": val
					}
				})
			elif ntk["val"] == "(" :
				pars = until("!)")
				if pars == None : exit(1)
				params = [[]]
				for i in pars :
					if i["val"] == "," :
						params.append([])
					else :
						params[-1].append(i)

				sections.append({
					"type": "funcCall",
					"fields": {
						"name": tkn["val"],
						"params": params,
					}
				})
			else :
				exit(1)
		elif tkn_val == "while" :
			cond = until("!{")
			res, _ = codeblock()
			sections.append({
				"type": "whileLoop",
				"fields": {
					"cond": cond,
					"res": res
				}
			})
		elif tkn_val == "include" :
			name = expect("string")
			if not name : exit(1)
			filename = name["val"].removeprefix('"').removesuffix('"')
			with open(filename) as f :
				text = f.read()
			sections.extend(
				parseSections(
					parseTokens(text)
				)
			)
		elif tkn_val == "for" :
			iden = expect("identifier")
			if not iden : exit(1)
			name = iden["val"]
			if not expect("!in") : exit(1)
			iterate = until("!{")
			res, _ = codeblock()
			sections.append({
				"type": "forLoop",
				"fields": {
					"name": name,
					"iter": iterate,
					"res": res
				}
			})
		elif tkn_val == "fn" :
			iden = expect("identifier")
			if not iden : exit(1)
			name = iden["val"]
			if not expect("!(") : exit(1)
			pars = until("!)")
			if pars == None : exit(1)
			params = [[]]
			for i in pars :
				if i["val"] == "," :
					params.append([])
				else :
					params[-1].append(i)
			params = [x for x in params if len(x) > 0]
			params = [{
				"val": x[1]["val"],
				"type": x[0]["val"]
			} for x in params]
			if not expect("!->") : exit(1)
			iden = expect("type")
			if not iden : exit(1)
			returnType = iden["val"]
			if not expect("!{") : exit(1)
			res, _ = codeblock()
			sections.append({
				"type": "funcDefine",
				"fields": {
					"name": name,
					"params": params,
					"return": returnType,
					"res": res
				}
			})
		elif tkn_val == "return" :
			start = line
			args = until("newline")
			if not args or len(args) == 0 :
				if err :
					err(start, "ExpectedValue", "Expected value after return statement", ["return"])
				tkn = getNext()
				continue

			pars = [[]]
			for i in args :
				if i["val"] != "," :
					pars[-1].append(i)
				else :
					pars.append([])
			pars = [x for x in pars if x]
			sections.append({
				"type": "returnStatement",
				"fields": {
					"params": pars,
				}
			})
		tkn = getNext()

	sections.sort(key=lambda x: precedence[x["type"]] if x["type"] in precedence else len(precedence))

	return sections
