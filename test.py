STDOUT: str = ""

def print_builtin(x) -> None :
	print(x)
	STDOUT = str(x) + "\n"

def input_builtin(msg: str) -> str :
	return input(msg)

x: int = 100

if x > 10:
	print_builtin(x) 
elif x > 5:
	print_builtin(5) 
elif x > 5:
	print_builtin(5)