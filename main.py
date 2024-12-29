
from termcolor import cprint

import json
from jsonformatter import formatJson, cleanJson

from errors import initError

from argsparser import parseAgrs

arguments, flags = parseAgrs({
	"t": "save-tokens",
	"s": "save-sections",
	"v": "save-vars",
	"r": "save-regex",
	"h": "help",
	"c": "compile"
})

if "help" in flags :
	print(
		"beanlang [file] [OPTIONS]",
		"",
		"OPTIONS :",
		" -r, --save-regex      Saves regex tokens in [filename]_regex.json",
		" -t, --save-tokens     Saves parsed tokens in [filename]_tokens.json",
		" -s, --save-sections   Saves parsed sections in [filename]_sections.json",
		" -v, --save-variables  Saves variables at every change in [filename]_variables.json",
		" -h, --help            Shows this message",
		sep = "\n"
	)
	exit()

filename = arguments[1]

with open(filename) as f :
	text = f.read()
	err_dumb = initError(text)

errors = 0
warnings = 0
def err(line: list[dict[str, str]] | int, errType: str, errMsg: str, under: list[str], error: bool = True) :
	global errors, warnings

	if error :
		errors += 1
	else :
		warnings += 1

	err_dumb(line, errType, errMsg, under, error)

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

def basePrint(x) :
	print(x["val"].strip("\""), end = "\n")
	scopes[0]["STDOUT"]["val"] = x["val"].strip("\"")

	return {
		"type": "void",
		"val": ""
	}

def baseInput(x) :
	grab = input(x["val"].strip("\""))

	if grab == "" :
		print("Input recieved was blank...")
		exit(1)

	return {
		"val": "\"" + grab + "\"",
		"type": "str"
	}

builtins = {
	"println": basePrint,
	"input": baseInput,
}

scopes = [
	{
		"STDOUT": {"val": '""', "type": "str", "const": True}
	}
]
for i in builtins :
	scopes[-1][i] = builtins[i]

from copy import deepcopy

all_scopes = [
	deepcopy(scopes)
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
def varDeclare(var_type: str, name: str, val: list[dict[str, str]], res: int = 0) :

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

	all_scopes.append(deepcopy(scopes))

@addHandler
def constDeclare(var_type: str, name: str, val: list[dict[str, str]], res: int = 0) :

	if name.startswith("_") :
		err(res, "BadName", f"Having a variable name start with an underscore is bad practice, use \"{name.lstrip("_")}\" instead", [name], False)

	if name.upper() != name :
		err(res, "NotSnakeCase", f"Variable name \"{name}\" is not uppercase, use \"{name.upper()}\"", [name], False)

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

	all_scopes.append(deepcopy(scopes))

@addHandler
def varUpdate(name: str, act: str, val: list[dict[str, str]], res: int = 0) :

	actual = deepcopy(val)

	if len(act) > 1 :
		actual.insert(0, {
			"val": act[0],
			"type": "Op"
		})
		actual.insert(0, {
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

	ret = evalExpr(actual)

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
			scopes[len(scopes) - n - 1][name] = {
				"val": ret["val"],
				"type": ret["type"],
				"const": False
			}
			break

	all_scopes.append(deepcopy(scopes))

@addHandler
def funcDefine(name: str, params: list[dict[str, str]], ret: str, body: list[dict], res: int = 0) :

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

	all_scopes.append(deepcopy(scopes))

@addHandler
def returnStatement(pars: list[list[dict[str, str]]], res: int = 0) -> list[dict[str, str]] | None :

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
		return func(*push)

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
def funcCall(name: str, params: list[list[dict[str, str]]], res: int = 0) :

	returns = callFunc(name, params)

	all_scopes.append(deepcopy(scopes))

	if type(returns) is tuple :
		err(res, returns[0], returns[1], [name])
		return

	if returns != None and returns["type"] != "void" :
		err(res, "UnusedReturn", f"Return value is unused", [name], False)

falsy = {
	"bool": "false",
	"str": '""',
	"int": "0",
	"float": "0.0"
}

@addHandler
def ifStatement(cond: list[dict[str, str]], body: list[dict], elif_body: list[dict], else_body: list[dict], res: int = 0) :

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

@addHandler
def whileLoop(cond: list[dict[str, str]], body: list[dict], res: int = 0) :
	if not [x for x in body if x["type"] == "varUpdate"] :
		err(res, "InfiniteLoop", "While loop contains no variable changes, it will be infinite", [])
		return

	ret = evalExpr(cond)

	if type(ret) is tuple :
		err(res, ret[0], ret[1], [x["val"] for x in cond])
		return
	if not(type(ret) is dict) : return

	while ret["val"] != falsy[ret["type"]] :
		for i in body :
			doSection(i)

		ret = evalExpr(cond)

		if type(ret) is tuple :
			err(res, ret[0], ret[1], [x["val"] for x in cond])
			return
		if not(type(ret) is dict) : return

@addHandler
def structDefine(name: str, params: list[list[dict[str, str]]], res: int = 0) :
	if name in scopes[-1] :
		err(res, "VariableRedeclare", f"Cannot redeclare var \"{name}\"", [name])
		return

	scopes[-1][name] = {
		"type": "struct",
		"val": "struct",
		"params": params
	}

@addHandler
def structDeclare(name: str, struct: str, params: list[list[dict[str, str]]], res: int = 0) :
	vars = {}
	for i in scopes :
		vars.update(i)
	if not struct in vars :
		err(res, "UndefinedVariable", f"Structure {struct} is undefined", [struct])
		return

def doSection(sec) :
	global errors

	sec_type = sec["type"]
	sec_fields = sec["fields"]

	passinto = list(sec_fields.values())
	passinto.append(sec["line"])

	if sec_type in handlers :
		return handlers[sec_type](
			*passinto
		)

	cprint(f"A section handler for sections of type \"{sec_type}\", has not been implemented", "red")
	errors += 1

for sec in sections :
	doSection(sec)

if "save-vars" in flags :
	with open(filename[:filename.rfind(".")] + "_variables.json", "w") as f :
		f.write(json.dumps(cleanJson(all_scopes)))

col = "green"
if warnings > 0 : col = "yellow"
if errors > 0 : col = "red"

cprint(f"\nProgram generated {warnings} warning(s) and {errors} error(s)", col)

from translater import translate

if "compile" in flags :
	if errors > 0 :
		cprint("Could not compile due to previous error(s)", "red")
		exit(1)

	if flags["compile"] == "" :
		print("Please specify a language to compile to")
		exit(1)

	translate(filename, sections, flags["compile"])
