
from tokenparser import parseTokens
from typing import Callable

precedence = {
	"constDeclare": 0,
	"structDefine": 1,
	"funcDefine": 2
}

line = 0
def parseSections(tokens: list[dict[str, str]], err: Callable | None = None) -> list[dict[str, dict]] :
	tokens.append({
		"val": "EOF",
		"type": "EOF"
	})
	sections: list[dict] = []
	grab = (x for x in tokens if not("comment" in x["type"].lower()))

	def getNext(newline: bool = True) :
		global line

		try :
			tkn = next(grab)
		except StopIteration :
			return {"val": "EOF", "type": "EOF"}

		if tkn["val"] == "\n" and newline :
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
			err(line, "UnexpectedToken", f"Expected {add}{token_type.removeprefix("!")}{add}, instead found {repr(tkn["val"])}", [tkn["val"]])

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

	def codeblock(newline: bool = True) -> tuple[list[dict[str, dict[str, str]]], dict[str, str]] :
		depth = 1
		block = []
		tkn = getNext(False)
		while depth > 0 :
			if tkn["val"] == "}" : depth -= 1
			if tkn["val"] == "{" : depth += 1
			if depth > 0 :
				block.append(tkn)
				tkn = getNext(False)
			else :
				tkn = getNext()

		return parseSections(block), tkn

	while tkn["type"] != "EOF" :

		tkn_type = tkn["type"]
		tkn_val = tkn["val"]

		sections.append({
			"line": line
		})

		if tkn_val == "struct" :
			name = expect("identifier")
			if not name : exit(1)
			expect("!{")
			depth = 1
			params = [[]]
			want = "type"
			while depth > 0 :
				ntk = getNext()
				if ntk["val"] == "}" : depth -= 1
				if ntk["val"] == "{" : depth += 1
				if depth > 0 and ntk["type"] != "newline" :
					if ntk["type"] != want and err :
						err(line, "UnexpectedToken", f"Expected {want}, instead found {repr(ntk["val"])}", [ntk["val"]])
					else :
						if ntk["val"] == "," :
							params.append([])
						else :
							params[-1].append(ntk)
					want = {
						"type": "identifier",
						"identifier": "argSplit",
						"argSplit": "type"
					}[want]
			sections[-1].update({
				"type": "structDefine",
				"fields": {
					"name": name["val"],
					"params": params
				}
			})
		elif tkn_type == "type" :
			ntk = getNext()
			const = False
			if ntk["val"] == "const" :
				const = True
				name = expect("identifier")
				if not name : exit(1)
			elif ntk["type"] == "identifier" :
				name = ntk
			else :
				if err :
					err(line, "UnexpectedToken", f"Expected identifier or \"const\", instead found \"{ntk["val"]}\"", [ntk["val"]])
				exit(1)
			nx = getNext()
			val = []
			if nx["val"] == "=" :
				val = until("newline")

			if const :
				sections[-1].update({
					"type": "constDeclare",
					"fields": {
						"type": tkn["val"],
						"name": name["val"],
						"val": val
					}
				})
			else :
				sections[-1].update({
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

			el = []
			if ntk["val"] == "else" :
				if not expect("!{") : exit(1)
				el, _ = codeblock()

			sections[-1].update({
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
				sections[-1].update({
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

				sections[-1].update({
					"type": "funcCall",
					"fields": {
						"name": tkn["val"],
						"params": params,
					}
				})
			elif ntk["type"] == "identifier" :
				if not expect("!="): exit(1)
				params = [[]]
				vals = until("newline")
				if not vals: exit(1)
				for i in vals :
					if i["val"] == "," :
						params.append([])
					else :
						params[-1].append(i)
				sections[-1].update({
					"type": "structDeclare",
					"fields": {
						"name": ntk["val"],
						"type": tkn["val"],
						"params": params,
					}
				})
			else :
				exit(1)
		elif tkn_val == "while" :
			cond = until("!{")
			res, _ = codeblock()
			sections[-1].update({
				"type": "whileLoop",
				"fields": {
					"cond": cond,
					"res": res
				}
			})
		elif tkn_val == "for" :
			iden = expect("identifier")
			if not iden : exit(1)
			name = iden["val"]
			if not expect("!in") : exit(1)
			iterate = until("!{")
			res, _ = codeblock()
			sections[-1].update({
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
			sections[-1].update({
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
			sections[-1].update({
				"type": "returnStatement",
				"fields": {
					"params": pars,
				}
			})
		tkn = getNext()

		if len(sections[-1].keys()) < 2 :
			sections.pop(-1)

	sections.sort(key=lambda x: precedence[x["type"]] if x["type"] in precedence else len(precedence))

	return sections
