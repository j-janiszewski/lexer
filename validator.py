import sys
import sys
from parser_ import Parser
from scanner import Scanner


if len(sys.argv) != 2:
    print("No path to file provided or too many arguments! ")
    print("Example of usage: 'python validator.py <path_to_file>'")
    quit()
else:
    file_path = sys.argv[1]


with open(file_path, "r") as f:
    test_file = f.read()

try:
    s = Scanner(test_file)
    p = Parser(s)
except Exception as ex:
    print("Program is not valid! More details about error:")
    print(ex)
else:
    print("Valid program")
