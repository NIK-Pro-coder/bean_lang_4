# Bean Lang v0.5.0
Bean Lang v0.5.0 is a silly little language that I've been writing for a few months.

It's syntax is designed to look like a mix between Python, C++ and a bit of Rust.

Please note that the error messages aren't really accurate, as they don't actually know what line the error occured in but try to guess it

## Command line options :
- `-t`, `--save-tokens` :
	Saves the tokens that have been parsed from the file
- `-r`, `--save-regex` :
	Saves all the regex matches that have been found in the file
- `-t`, `--save-tokens` :
	Saves the tokensa that have been parsed from the file
- `-s`, `--save-sections` :
	Saves the sections that have been parsed from the file
- `-v`, `--save-vars` :
	Every time a variable is created or changed adds an entry to this file, sort of like a timestamp
- `-c`, `--compile` `[lang]` :
	Translates the file into the specified language, use language templates for this (more on them in the future)

## Expression symbols :

Most symbols in Bean Lang are the same as the ones in Python, a few exceptions are :
- `a ^ b` : Raises a to the power of b (eg. `3 ^ 2` -> `9`)
- `a & b` : Logical and between a and b (eg. `true & false` -> `false`)
- `a | b` : Logical or between a and b (eg. `true | false` -> `true`)
- `a >< b` : Joins a and b as string (eg. `10 >< " hi"` -> `"10 hi"`)
- `a && b` : Bitwise and between a and b (eg. `3 && 2` -> `1`)
- `a || b` : Bitwise or between a and b (eg. `3 || 2` -> `3`)
- `a ^^ b` : Bitwise xor between a and b (eg. `3 ^ 2` -> `1`)

The symbols for logical and and logical or are swapped with bitwise and and bitwise or because you'd normally use them more

## Syntax examples :

- Comment :
	```
	short comment : # [comment]
	long comment : /* [comment] */
	```
	Comments are an essential part of programming (I don't use them much)
	The short comment syntax is borrowed from Python, the long coment is borrowed from C++/Rust

	### Examples :
	```
	# This is a single-line comment
	int y = 300 # <- this will run

	/*
	This is a long comment
	int x = 10 <- this will not run
	*/
	```

- Variable declaration :
	```
	[type] [const] [name] = [expr]
	```

	A variable is one of the building blocks of programming languages so I made sure that they are relatively simple

	### Examples :
	```
	int x = 300
	str const y = "Hello, world"

	float z = 50 / 3
	```

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

- While loop :
	```
	while [expr] {
		[code block]
	}
	```

	A while loop is the simples loop in programming, it simply repeats the code block while the condition is true

	### Examples :
	```
	int x = 300

	while x > 0 {
		print("x is " >< x)
		x -= 1
	}
	```

- Function definitions :
	```
	fn [name] ([type] [argname]) -> [return type] {
		[code block]
	}
	```
	Here I borrowed a bit from Rust (`fn` keyword) and Python (`->` for return type).

	Please note that redefining a function with different parameters will automaticaly create an overload

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

## Builtin functions :
- print

	The `print()` function takes one argument and prints it to stdout, it also saves it in a variable named `STDOUT`

- input

	The `input()` function prompts the user for an input and returns it as a string

- other function coming soon ;)
