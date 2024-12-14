
precedence = {
	"^": 0,
	"%": 1,
	"*": 2,
	"/": 2,
	"+": 3,
	"-": 3,
	"><": 4,
	"&": 6,
	"|": 6,
	"==": 5,
	"!=": 5,
	">=": 5,
	"<=": 5,
	"<": 5,
	">": 5,
}
def infixToPostfix(tokens: list[dict[str, str]]) -> list[dict[str, str]] :
	postfix = []
	stack = []

	for i in tokens :

		if i["val"] == "(" :
			stack.append(i)
		elif i["val"] == ")" :
			while stack[-1]["val"] != "(" :
				postfix.append(stack.pop(-1))
			stack.pop(-1)
		elif "Op" in i["type"] :
			if len(stack) == 0 :
				stack.append(i)
			elif stack[-1]["val"] == "(" :
				stack.append(i)
			elif precedence[i["val"]] < precedence[stack[-1]["val"]] :
				stack.append(i)
			else :
				while precedence[i["val"]] >= precedence[stack[-1]["val"]] :
					postfix.append(stack.pop(-1))
					if len(stack) == 0 : break
				stack.append(i)
		else :
			postfix.append(i)

	postfix.extend(stack[::-1])

	return postfix

operands = {
	"+": {
		"int int": lambda x,y : {
			"val": str(
				int(x) + int(y)
			),
			"type": "int"
		},
		"int float": lambda x,y : {
			"val": str(
				float(x) + float(y)
			),
			"type": "float"
		},
		"float float": lambda x,y : {
			"val": str(
				float(x) + float(y)
			),
			"type": "float"
		},
		"str str": lambda x,y : {
			"val": '"' +x[1:-1] + y[1:-1] + '"',
			"type": "str"
		},
	},
	"-": {
		"int int": lambda x,y : {
			"val": str(
				int(x) - int(y)
			),
			"type": "int"
		},
		"int float": lambda x,y : {
			"val": str(
				float(x) - float(y)
			),
			"type": "float"
		},
		"float float": lambda x,y : {
			"val": str(
				float(x) - float(y)
			),
			"type": "float"
		},
	},
	"*": {
		"int int": lambda x,y : {
			"val": str(
				int(x) * int(y)
			),
			"type": "int"
		},
		"int float": lambda x,y : {
			"val": str(
				float(x) * float(y)
			),
			"type": "float"
		},
		"float float": lambda x,y : {
			"val": str(
				float(x) * float(y)
			),
			"type": "float"
		},
	},
	"/": {
		"int int": lambda x,y : {
			"val": str(
				int(int(x) / int(y)) if int(int(x) / int(y)) == int(x) / int(y) else int(x) / int(y)
			),
			"type": "int" if int(int(x) / int(y)) == int(x) / int(y) else "float"
		},
		"int float": lambda x,y : {
			"val": str(
				float(x) / float(y)
			),
			"type": "float"
		},
		"float float": lambda x,y : {
			"val": str(
				float(x) / float(y)
			),
			"type": "float"
		},
	},
	"^": {
		"int int": lambda x,y : {
			"val": str(
				int(x) ** int(y)
			),
			"type": "int"
		},
		"int float": lambda x,y : {
			"val": str(
				float(x) ** float(y)
			),
			"type": "float"
		},
		"float float": lambda x,y : {
			"val": str(
				float(x) ** float(y)
			),
			"type": "float"
		},
	},
	"%": {
		"int int": lambda x,y : {
			"val": str(
				int(x) % int(y)
			),
			"type": "int"
		},
		"int float": lambda x,y : {
			"val": str(
				float(x) % float(y)
			),
			"type": "float"
		},
		"float float": lambda x,y : {
			"val": str(
				float(x) % float(y)
			),
			"type": "float"
		},
	},
	"==": {
		"* *": lambda x,y : {
			"type": "bool",
			"val": "true" if x == y else "false"
		}
	},
	"!=": {
		"* *": lambda x,y : {
			"type": "bool",
			"val": "true" if x != y else "false"
		}
	},
	">=": {
		"* *": lambda x,y : {
			"type": "bool",
			"val": "true" if x >= y else "false"
		}
	},
	"<=": {
		"* *": lambda x,y : {
			"type": "bool",
			"val": "true" if x <= y else "false"
		}
	},
	">": {
		"* *": lambda x,y : {
			"type": "bool",
			"val": "true" if x > y else "false"
		}
	},
	"<": {
		"* *": lambda x,y : {
			"type": "bool",
			"val": "true" if x < y else "false"
		}
	},
	"&" : {
		"bool bool": lambda x,y : {
			"type": "bool",
			"val": "true" if x == "true" and y == "true" else "false"
		}
	},
	"|" : {
		"bool bool": lambda x,y : {
			"type": "bool",
			"val": "true" if x == "true" or y == "true" else "false"
		}
	},
	"><": {
		"* *" : lambda x,y : {
			"type": "str",
			"val": '"' + (x[1:-1] if x[0] == '"' and x[-1] == '"' else x) + (y[1:-1] if y[0] == '"' and y[-1] == '"' else y) + '"'
		}
	}
}
def evalInfix(infix: list[dict[str, str]]) -> dict[str, str] | tuple[str, str] :
	stack = []

	for i in infix :
		if "Op" in i["type"] :
			if len(stack) < 2 :
				return "MissingSide", f"Operator \"{i["val"]}\" is missing an operand"

			right, left = stack.pop(-1), stack.pop(-1)

			type_l, type_r = left["type"], right["type"]
			val_l, val_r = left["val"], right["val"]

			op = operands[i["val"]]

			possible = [
				"* *",
				f"{type_l} *",
				f"{type_r} *",
				f"{type_l} {type_r}",
				f"{type_r} {type_l}",
			]

			defined = any([x in op for x in possible])

			if not defined : return "UndefinedOperation", f"Operation \"{i["val"]}\" is not defined for types \"{type_l}\" and \"{type_r}\""

			func = None
			for p in possible :
				if p in op : func = op[p]

			if not func : return "UndefinedOperation", f"Operation \"{i["val"]}\" is not defined for types \"{type_l}\" and \"{type_r}\""

			stack.append(func(val_l, val_r))
		else :
			stack.append(i)

	if len(stack) > 1 :
		return "TooLittleOperations", "Expression eval stack contains more that one element, perhaps you forgot an operator?"

	return stack[0]
