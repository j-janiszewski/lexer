# Stylesheets parser

Project for the course "Formal languages and compilers" at Warsaw University of Technology 2023. The project aimed to create a parser for a fictional programming language. 

The parser should carry out a lexical analysis of the program and, if it is incorrect, inform you in which line and column the error is located.


## Example of a valid program

```
// this is a comment correct.ppap
#abc
	background: url(watch?v=Ct6BUPvE2sM);
	color: #f00;
	box-shadow: none;
	text-shadow: none;

.def
	content: "see below";

p > pre
	border: 1px solid #999;
	page-break-inside: avoid;

div + p,
div > p
	font-weight: bolder

p img
	max-width: 100% !important;

pine + apple,
* + * // * is a valid id
	orphans: 3;
	widows: 3rem;

a:visited
	color: white;


```

## Example of a non-valid program

```
p + + q // operators (np. +, >) cannot appear more than once between id's
	content: "see below";
	border: 1px solid #999;
	page-break-inside: avoid;

div+p,
div>p
  font-size: smaller; // too small indendation
		font-family: serif; //too big indendation
	font-weight: bolder; // here is ok
	font-style: normal; 

pine + apple
	max-width: 100% !oops; // only  !important can have !

foo _bar, // valid id
&baz, // non-valid id
:quax // valid id
	display: flex // semicolon must be present between attributes
	margin: 1px // lack of semicolon is ok at the end

```

## How to use it?

Pass path to program that should be validated to validator.py

```console
python validator.py <program-path>
```

If program is valid "Valid program" will be printed to console if not information about an error.
