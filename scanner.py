import re
from dataclasses import dataclass


TOKEN_PATTERNS = {
    "ATTR_NAME": re.compile(r"content"),
    "COLON": re.compile(r":"),
    "VALUE": re.compile(r'".*"'),
    "OPERATOR": re.compile(r"\+|>"),
    "COMMA": re.compile(r","),
    "ID": re.compile(r"\*|(#|\.)*[a-zA-Z._]*:*[a-zA-Z._]+"),
    "SPACE": re.compile(r" "),
    "NEWLINE": re.compile(r"\n"),
    "INDENT": re.compile(r"\t")
    #  "COMMENT": re.compile
}

IGNORED = ["SPACE", "COMMENT"]


@dataclass
class Token:
    name: str
    value: str
    line_number: int
    column: int


class Scanner:
    def __init__(self, input_file) -> None:
        self.tokens_read = []
        self.indent_level = 0
        line_no = 0
        while input_file:
            token_name, end, value = self.try_to_match(input_file)
            if token_name not in IGNORED:
                self.tokens_read.append(Token(token_name, value, line_no))
            if token_name == "NEWLINE":
                line_no += 1
            input_file = input_file[end:]

    def try_to_match(self, input):
        for token_name, regex in TOKEN_PATTERNS.items():
            match = regex.match(input)
            if match:
                print(token_name)
                return token_name, match.end(), match.group()
        print("couldnt match", input)
