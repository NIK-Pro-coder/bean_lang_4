
import sys

def parseAgrs(alias: dict[str, str] = {}) -> tuple[list[str], dict[str, str]] :
	args = []
	flag = {}

	last_flag = ""
	for i in sys.argv :
		if i.startswith("-") :
			if i.startswith("--") :
				last_flag = i.lstrip("-")
				flag[i.lstrip("-")] = ""
			else :
				flags = i.lstrip("-")
				for f in flags :
					if f in alias :
						f = alias[f]
					last_flag = f
					flag[f] = ""
		elif last_flag != "" :
			flag[last_flag] = i
		else :
			args.append(i)

	return args, flag
