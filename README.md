# Bean Lang V4
Bean Lang V4 is a silly little language that I've been writing for a few months.
It's syntax is designed to look like a mix between Python, C++ and a bit of Rust.

---

## Following are a few syntax examples :

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
