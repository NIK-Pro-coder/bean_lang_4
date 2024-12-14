import json

# This function simply formats a json
def formatJson(obj) :
	js = json.dumps(obj)
	new = ""
	depth = 0
	for i in js :
		if i in ["]","}"] :
			depth -= 1
			new += "\n" + "  " * depth

		new += i

		if i in ["[","{"] : depth += 1
		if i in ["[","{",","] : new += "\n" + "\t" * depth

	return new.replace("\t ", "\t").replace("\t", "  ")

def cleanJson(js) :
	if callable(js) :
		return "Function"

	if type(js) is dict :
		cl = {}
		for i in js :
			cl[cleanJson(i)] = cleanJson(js[i])
		return cl
	if type(js) is list :
		return [cleanJson(x) for x in js]

	return js
