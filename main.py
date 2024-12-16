
import json
from os import removexattr
from jsonformatter import formatJson, cleanJson

from errors import initError

from argsparser import parseAgrs

arguments, flags = parseAgrs({
	"t": "save-tokens",
	"s": "save-sections",
	"v": "save-vars",
	"r": "save-regex",
	"h": "help"
})

if "help" in flags :
	print(
		"beanlang [file] [OPTIONS]",
		"",
		"OPTIONS :",
		" -r, --save-regex      Saves regex tokens in [filename]_regex.json",
		" -t, --save-tokens     Saves parsed tokens in [filename]_tokens.json",
		" -s, --save-sections   Saves parsed sections in [filename]_sections.json",
		" -v, --save-variables  Saves variables in global scope in [filename]_variables.json",
		" -h, --help            Shows this message",
		sep = "\n"
	)
	exit()

filename = arguments[1]

with open(filename) as f :
	text = f.read()
	err = initError(text)

from sectionparser import parseSections
from tokenparser import parseTokens

tokens, regex = parseTokens(text, "save-regex" in flags)

if "save-regex" in flags :
	with open(filename[:filename.rfind(".")] + "_regex.json", "w") as f :
		f.write(json.dumps(regex))

if "save-tokens" in flags :
	with open(filename[:filename.rfind(".")] + "_tokens.json", "w") as f :
		f.write(json.dumps(tokens))

sections = parseSections(tokens, err)

if "save-sections" in flags :
	with open(filename[:filename.rfind(".")] + "_sections.json", "w") as f :
		f.write(json.dumps(sections))

from infixhandler import infixToPostfix, evalInfix

handlers = {}
def addHandler(func) :
	handlers[func.__name__] = func

scopes = [
	{
		"print": (lambda x : print(x["val"], end = ""))
	}
]

def evalExpr(expr: list[dict[str, str]]) -> dict[str, str] | tuple[str, str] :

	vars = {}

	for i in scopes :
		vars.update(i)

	fnname = ""
	inputs = []
	depth = 0
	getting = False

	parse = []

	for n, i in enumerate(expr) :
		if getting:
			if i["val"] == ")" : depth -= 1

			if depth > 0 :
				inputs.append(i)

			if i["val"] == "(" : depth += 1

			if depth == 0 :
				getting = False
				params = [[]]
				for p in inputs :
					if p["val"] == "," :
						params.append([])
					else :
						params[-1].append(p)
				params = [x for x in params]
				returns = callFunc(fnname, params)

				if type(returns) is tuple : return returns

				if returns != None :
					parse.append(returns)

			continue

		if i["type"] == "identifier" :
			if n < len(expr) - 2 and expr[n+1]["val"] == "(" :
				fnname = i["val"]
				depth = 0
				getting = True
			else :
				if not i["val"] in vars :
					return "UndefinedVariable", f"Variable \"{i["val"]}\" is not defined"

				parse.append(vars[i["val"]])
		else :
			parse.append(i)

	infix = infixToPostfix(parse)

	ret = evalInfix(infix)

	return ret

@addHandler
def varDeclare(var_type: str, name: str, val: list[dict[str, str]]) :
	res = [
		{"val": var_type, "type": "type"},
		{"val": name, "type": "identifier"},
	]
	if val :
		res.append({
			"val": "=",
			"type": "assign"
		})
		res.extend(val)

	if name.startswith("_") :
		err(res, "BadName", f"Having a variable name start with an underscore is bad practice, use \"{name.lstrip("_")}\" instead", [name], False)

	if name.lower() != name :
		snake = "".join([("_" if x != x.lower() else "") + x.lower() for x in name]).replace("__", "_")

		err(res, "NotSnakeCase", f"Variable name \"{name}\" is not snake case, use \"{snake}\"", [name], False)

	if name in scopes[-1] :
		err(res, "VariableRedeclare", f"Cannot redeclare var \"{name}\"", [name])
		return

	ret = evalExpr(val)

	if type(ret) is tuple :
		err(res, ret[0], ret[1], [x["val"] for x in val])
		return

	if not type(ret) is dict : return

	ret_type = ret["type"]

	if var_type != ret_type :
		err(res, "MismatchedTypes", f"Cannot assign {ret["val"]} ({ret_type}) to var of type {var_type}", [x["val"] for x in val])
		return

	if ret["type"] == "func" :
		scopes[-1][name] = {
			"val": "function",
			"type": "func",
			"const": True,
			"over": ret["over"]
		}
	else :
		scopes[-1][name] = {
			"val": ret["val"],
			"type": ret["type"],
			"const": False
		}

@addHandler
def constDeclare(var_type: str, name: str, val: list[dict[str, str]]) :
	res = [
		{"val": var_type, "type": "type"},
		{"val": name, "type": "identifier"},
	]
	if val :
		res.append({
			"val": "=",
			"type": "assign"
		})
		res.extend(val)

	if name.startswith("_") :
		err(res, "BadName", f"Having a variable name start with an underscore is bad practice, use \"{name.lstrip("_")}\" instead", [name], False)

	if name.lower() != name :
		snake = "".join([("_" if x != x.lower() else "") + x.lower() for x in name]).replace("__", "_")

		err(res, "NotSnakeCase", f"Variable name \"{name}\" is not snake case, use \"{snake}\"", [name], False)

	if name in scopes[-1] :
		err(res, "VariableRedeclare", f"Cannot redeclare var \"{name}\"", [name])
		return

	ret = evalExpr(val)

	if type(ret) is tuple :
		err(res, ret[0], ret[1], [x["val"] for x in val])
		return

	if not type(ret) is dict : return

	ret_type = ret["type"]

	if var_type != ret_type :
		err(res, "MismatchedTypes", f"Cannot assign {ret["val"]} ({ret_type}) to var of type {var_type}", [x["val"] for x in val])
		return

	if ret["type"] == "func" :
		scopes[-1][name] = {
			"val": "function",
			"type": "func",
			"const": True,
			"over": ret["over"]
		}
	else :
		scopes[-1][name] = {
			"val": ret["val"],
			"type": ret["type"],
			"const": True
		}

@addHandler
def varUpdate(name: str, act: str, val: list[dict[str, str]]) :
	res = [
		{"val": name, "type": "identifier"},
		{"val": act, "type": "assign"},
	]
	res.extend(val)

	if len(act) > 1 :
		val.insert(0, {
			"val": act[0],
			"type": "Op"
		})
		val.insert(0, {
			"val": name,
			"type": "identifier"
		})

	vars = {}

	for i in scopes :
		vars.update(i)

	if not name in vars :
		err(res, "UndefinedVariable", f"Variable \"{name}\" is not defined", [name])
		return

	if vars[name]["const"] :
		err(res, "UpdateConstant", f"Variable \"{name}\" has been defined as constant, need I say more?", [name])
		return

	var_type = vars[name]["type"]

	ret = evalExpr(val)

	if type(ret) is tuple :
		err(res, ret[0], ret[1], [x["val"] for x in val])
		return

	if not type(ret) is dict : return

	ret_type = ret["type"]

	if var_type != ret_type :
		err(res, "MismatchedTypes", f"Cannot assign {ret["val"]} ({ret_type}) to var of type {var_type}", [x["val"] for x in val])
		return

	for n,i in enumerate(scopes[::-1]) :
		if name in i :
			scopes[len(scopes) - n - 1][name] = ret
			break

@addHandler
def funcDefine(name: str, params: list[dict[str, str]], ret: str, body: list[dict]) :
	res = [
		{"val": "fn", "type": "keyword"},
		{"val": name, "type": "identifier"},
		{"val": "(", "type": "parenteses"}
	]
	for i in params :
		res.append(
			{"val": i["type"], "type": "type"}
		)
		res.append(
			{"val": i["val"], "type": "identifier"}
		)
	res.append({"val": ")", "type": "parenteses"})
	res.append({"val": "->", "type": "return"})
	res.append({"val": ret, "type": "type"})
	res.append({"val": "{", "type": "parenteses"})
	if len(body) == 0 :
		res.append({"val": "}", "type": "parenteses"})

	if not(name in scopes[-1]) :
		scopes[-1][name] = {
			"type": "func",
			"over": [],
			"const": True,
			"val": "Function"
		}

	if params in [x["params"] for x in scopes[-1][name]["over"]] :
		err(res, "OverloadExists", f"Overload for func \"{name}\" already exists with params: {" ,".join([x["type"] for x in params])}", [x["val"] for x in params])
		return

	scopes[-1][name]["over"].append({
		"params": params,
		"res": body,
		"ret": ret,
	})

@addHandler
def returnStatement(pars: list[list[dict[str, str]]]) -> list[dict[str, str]] | None :
	res = [
		{"val": "return", "type": "keyword"}
	]
	for i in pars :
		res.extend(i)
		res.append({"val": ",", "type": "argSplit"})
	res.pop(-1)

	if len(scopes) == 1 :
		err(res, "BaseLevelReturn", "Returning from global scope doesn't really do anything", [x["val"] for x in res], False)
		return

	give = []
	for val in pars :
		ret = evalExpr(val)

		if type(ret) is tuple :
			err(res, ret[0], ret[1], [x["val"] for x in val])
			return

		give.append(ret)

	return give[0]

def callFunc(name: str, params: list[list[dict[str, str]]]) -> None | list[dict[str, str]] | tuple[str, str] :
	vars = {}

	for i in scopes :
		vars.update(i)

	if not name in vars :
		return "UndefinedVariable", f"Variable \"{name}\" is not defined"

	func = vars[name]

	push = []
	for val in params :
		ret = evalExpr(val)

		if type(ret) is tuple :
			return ret

		if not type(ret) is dict : return

		push.append(ret)

	if callable(func) :
		func(*push)
		return

	in_types = [x["type"] for x in push]
	over_types = [[y["type"] for y in x["params"]] for x in func["over"]]

	if not in_types in over_types :
		flat = []
		for i in params :
			flat.extend([x["val"] for x in i])
		return "UndefinedOverload", f"Function \"{name}\" has no overload with params: {", ".join(in_types)}"

	call = func["over"][over_types.index(in_types)]

	scopes.append({})

	for n,i in enumerate(call["params"]) :
		handlers["varDeclare"](i["type"], i["val"], [push[n]])

	returns = None
	for i in call["res"] :
		give = doSection(i)
		if i["type"] == "returnStatement" :
			returns = give
			break

	scopes.pop(-1)

	if returns and returns["type"] != call["ret"] :
		return "MismatchedTypes", f"Expected a return type of {call["ret"]}, instead found {returns["type"]}"

	return returns

@addHandler
def funcCall(name: str, params: list[list[dict[str, str]]]) :
	res = [
		{"val": name, "type": "identifier"},
		{"val": "(", "type": "parenteses"}
	]
	for i in params :
		res.extend(i)
	res.append({"val": ")", "type": "parenteses"})

	returns = callFunc(name, params)

	if type(returns) is tuple :
		err(res, returns[0], returns[1], [name])
		return

	if returns != None :
		err(res, "UnusedReturn", f"Return value is unused", [name], False)

falsy = {
	"bool": "false",
	"str": '""',
	"int": "0",
	"float": "0.0"
}

@addHandler
def ifStatement(cond: list[dict[str, str]], body: list[dict], elif_body: list[dict], else_body: list[dict]) :
	res = [
		{"val": "if", "type": "identifier"}
	]
	res.extend(cond)
	res.append({"val": "{", "type": "parenteses"})

	ret = evalExpr(cond)

	if type(ret) is tuple :
		err(res, ret[0], ret[1], [x["val"] for x in cond])
		return
	if not(type(ret) is dict) : return

	if ret["val"] != falsy[ret["type"]] :
		for i in body :
			doSection(i)
	else :
		for e in elif_body :
			ret = evalExpr(e["cond"])

			print(e["cond"])
			print(ret)

			if type(ret) is tuple :
				err(res, ret[0], ret[1], [x["val"] for x in cond])
				return
			if not(type(ret) is dict) : return

			if ret["val"] != falsy[ret["type"]] :
				for i in e["res"] :
					doSection(i)
				return

		for i in else_body :
			doSection(i)

def doSection(sec) :
	sec_type = sec["type"]
	sec_fields = sec["fields"]

	return handlers[sec_type](
		*sec_fields.values()
	)

for sec in sections :
	doSection(sec)

if "save-vars" in flags :
	with open(filename[:filename.rfind(".")] + "_variables.json", "w") as f :
		f.write(json.dumps(cleanJson(scopes)))
