import re
from dataclasses import dataclass


# FIXME: background: url(watch?v=Ct6BUPvE2sM); couses an error
TOKEN_PATTERNS = {
    "PROPERTY_NAME": re.compile(r"[a-zA-Z\-]+:"),
    "TEXT_VALUE": re.compile(r'".*"'),
    "HEX_VALUE": re.compile(r"#[ABCDEF0-9]+"),
    "REM_VAlUE": re.compile(r"[0-9]+em"),
    "%_VALUE": re.compile(r"[0-9]+%"),
    "INT_VALUE": re.compile(r"[0-9]+"),
    "URL_VALUE": re.compile(r"url\([0-9a-zA-Z\?=_:;-]+\)"),
    "OPERATOR": re.compile(r"\+|>"),
    "ID": re.compile(r"\*|(#|\.)*[a-zA-Z._]*:*[a-zA-Z._]+"),
    "IMPORTANT": re.compile(r"!important"),
    "COMMENT": re.compile(r"\/\/[^\n]*"),
    "SEMICOLON": re.compile(r";"),
    "COMMA": re.compile(r","),
    "SPACE": re.compile(r" "),
    "NEWLINE": re.compile(r"\n"),
    "INDENTATION": re.compile(r"\t+"),
}

IGNORED = ["SPACE", "COMMENT", "NEWLINE", "INDENTATION"]


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
        self.line_number = 0
        self.column_number = 0
        while input_file:
            token_name, value, end = self.try_to_match(input_file)
            # if column_number is zero that means that we are starting to analyze new line of program
            # in this place i handle indentation
            if self.column_number == 0:
                self.handle_indendations(token_name, value)

            if token_name not in IGNORED:
                self.add_new_token(token_name, value)
            if token_name == "NEWLINE":
                self.line_number += 1
                self.column_number = 0
            else:
                self.column_number += end
            input_file = input_file[end:]
        else:
            self.handle_indendations("EOF", "")
            self.add_new_token("EOF", "")

    def try_to_match(self, input):
        """
        Finds matching Token from TOKEN_PATTERNS in the begging of input
        or throws RuntimeError if there is no such.

        Args:
            input (str): input where token is sought

        Returns:
            tuple[str, str, int]: tuple with token_name, token_value and ending column number
        """
        for token_name, regex in TOKEN_PATTERNS.items():
            match = regex.match(input)
            if match:
                return token_name, match.group(), match.end()
        raise RuntimeError(
            f"Error: Unexpected character {input} on line {self.line_number}"
        )

    def handle_indendations(self, token_name, token_value):
        """
        Checks indendation levels in new line and compares it to indentation_level attribute.
        Generates INDENT and DEDENT Tokens if needed.

        Args:
            token_name (str): current Token name
            token_value (str): current Token value
        """
        if token_name == "INDENTATION":
            number_of_tabs = token_value.count("\t")
            if number_of_tabs > self.indent_level:
                for _ in range(number_of_tabs - self.indent_level):
                    self.add_new_token("INDENT", "indentation")
                    self.indent_level += 1
            elif number_of_tabs < self.indent_level:
                self.dedent_n_times(self.indent_level - number_of_tabs)
        elif self.indent_level != 0:
            self.dedent_n_times(self.indent_level)

    def dedent_n_times(self, n):
        """Adds DEDENT Token and reduces indentation n times

        Args:
            n (int): number of DEDENT's
        """
        for _ in range(n):
            self.add_new_token("DEDENT", "dedentation")
            self.indent_level -= 1

    def add_new_token(self, token_name, token_value):
        """Appends token_read attribute with new Token

        Args:
            token_name (str): new Token name
            token_value (str): new Token value
        """
        self.tokens_read.append(
            Token(token_name, token_value, self.line_number, self.column_number)
        )
