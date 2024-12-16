# Bean Lang V4
Bean Lang V4 is a silly little language that I've been writing for a few months.
It's syntax is designed to look like a mix between Python, C++ and a bit of Rust.

---

## Expression symbols :

Bitwise operations are coming soon

Most symbols in Bean Lang are the same as the ones in Python, a few exceptions are :
- `a ^ b` : Raises a to the power of b
- `a & b` : Logical and between a and b
- `a | b` : Logical or between a and b
- `a >< b` : Joins a and b as string (eg. `10 >< " hi"` -> `"10 hi"`)

## Syntax examples :

- Comment :
	```
		short comment : # [comment]
		long comment : /* [comment] */
	```
	Comments are an essential part of programming (I don't use them)
	The short comment syntax is borrowed from Python, the long coment is borrowed from C++/Rust

	---
	### Examples :
	```
	# This is a single-line comment
	int y = 300 # <- this will run

	/*
	This is a long comment
	int x = 10 <- this will not run
	*/
	```
	---

- Variable declaration :
	```
	[type] [const] [name] = [expr]
	```

	A variable is one of the building blocks of programming languages so I made sure that they are relatively simple

	---
	### Examples :
	```
	int x = 300
	str const y = "Hello, world"

	float z = 50 / 3
	```
	---

- If statement :
	```
	if [expr] {
		[code block]
	} [elif] [cond] {
		[code block]
	} [else] {
		[code block]
	}
	```

	If statements are quite important as they are the first step towards Turing-completeness, that said, I implemented them yesterday

	---
	### Examples :
	```
	if x > 100 {
		print("hello")
	}

	if y != "ciao" {
		print("this")
	} else {
		print("that")
	}

	if z == 1 {
		print("z is 1")
	} elif z == 2 {
		print("z is 2")
	} elif z == 2 {
		print("z is 3")
	} else {
		print("z is " >< z)
	}
	```
	---

- While loop :
	```
	while [expr] {
		[code block]
	}
	```

	A while loop is the simples loop in programming, it simply repeats the code block while the condition is true

	---
	### Examples :
	```
	int x = 300

	while x > 0 {
		print("x is " >< x)
		x -= 1
	}
	```
	---

- Function definitions :
	```
	fn [name] ([type] [argname]) -> [return type] {
		[code block]
	}
	```
	Here I borrowed a bit from Rust (`fn` keyword) and Python (`->` for return type).

	Please note that redefining a function with different parameters will automaticaly create an overload

	---
	### Examples :
	```
	fn addten(int x) -> int {
		return x + 10
	}
	fn addten(float x) -> float {
		return x + 10
	}

	addten(10)  # will call the first function
	addten(3.5) # will call the second function
	```
	---

## Builtin functions :
- print

	The `print()` function takes one argument and prints it to stdout, it also saves it in a variable named `STDOUT`

- input

	The `input()` function prompts the user for an input and returns it as a string

- other function coming soon ;)
