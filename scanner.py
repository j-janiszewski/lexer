import re
from dataclasses import dataclass
from enum import Enum


class TokenNames(Enum):
    PROPERTY_NAME = re.compile(r"[a-zA-Z\-]+: ")
    REM_VAlUE = re.compile(r"[0-9]+rem")
    URL_VALUE = re.compile(r"url\([0-9a-zA-Z\?=_:;-]+\)")
    ID = re.compile(r"\*|(#|\.)*[a-zA-Z._]*:*[a-zA-Z._]+")
    HEX_VALUE = re.compile(r"#[ABCDEFabcdefS0-9]{3}")
    TEXT_VALUE = re.compile(r'".*"')
    PERC_VALUE = re.compile(r"[0-9]+%")
    PX_VALUE = re.compile(r"[1-9]+[0-9]*px")
    INT_VALUE = re.compile(r"[0-9]+")
    OPERATOR = re.compile(r"\+|>")
    IMPORTANT = re.compile(r"!important")
    COMMENT = re.compile(r"\/\/[^\n]*")
    SEMICOLON = re.compile(r";")
    COMMA = re.compile(r",")
    SPACE = re.compile(r" ")
    NEWLINE = re.compile(r"\n")
    INDENTATION = re.compile(r"\t+")
    EOL = ""
    INDENT = ""
    DEDENT = ""


IGNORED = [TokenNames.SPACE, TokenNames.COMMENT, TokenNames.INDENTATION]
ADDED_BY_SCANNER = [TokenNames.EOL, TokenNames.INDENT, TokenNames.DEDENT]


@dataclass
class Token:
    name: str
    value: str
    line: int
    column: int


class UnexpectedTokenException(Exception):
    def __init__(self, token, line, column) -> None:
        super().__init__(
            f" Unexpected token: `{token}` \n on line: {line}, column: {column}"
        )


class Scanner:
    def __init__(self, input_file) -> None:
        self.tokens_read: list[Token] = []
        self.indent_level = 0
        self.line = 1
        self.column = 0
        while input_file:
            token_name, value, end = self.try_to_match(input_file)
            # if column_number is zero that means that we are starting to analyze new line of program
            # in this place i handle indentation
            if self.column == 0:
                self.handle_indendations(token_name, value)
            if len(self.tokens_read) != 0:
                if (
                    self.tokens_read[-1].name == TokenNames.INDENT
                    or self.tokens_read[-1].name == TokenNames.DEDENT
                ) and token_name == TokenNames.SPACE:
                    raise IndentationError(
                        f"Only tabs can be used for indendation, Whitespace character on line: {self.line}, column: {self.column}"
                    )

            if token_name not in IGNORED:
                self.add_new_token(token_name, value)
            if token_name == TokenNames.NEWLINE:
                self.line += 1
                self.column = 0
            else:
                self.column += end
            input_file = input_file[end:]
        else:
            self.handle_indendations(TokenNames.EOL, "")
            self.add_new_token(TokenNames.EOL, "")

    def try_to_match(self, input):
        """
        Finds matching Token from TOKEN_PATTERNS in the begging of input
        or throws RuntimeError if there is no such.

        Args:
            input (str): input where token is sought

        Returns:
            tuple[str, str, int]: tuple with token_name, token_value and ending column number
        """
        for token_name in TokenNames:
            if token_name in ADDED_BY_SCANNER:
                continue
            match = token_name.value.match(input)
            if match:
                # handling case when begging of hex i matched with ID
                if token_name == TokenNames.ID and len(input) != match.end():
                    if input[match.end()].isdigit():
                        continue
                return token_name, match.group(), match.end()
        raise UnexpectedTokenException(input.split()[0], self.line, self.column)

    def handle_indendations(self, token_name, token_value):
        """
        Checks indendation levels in new line and compares it to indentation_level attribute.
        Generates INDENT and DEDENT Tokens if needed.

        Args:
            token_name (str): current Token name
            token_value (str): current Token value
        """
        if token_name == TokenNames.SPACE:
            raise IndentationError(
                f"Only tabs can be used for indendation, Whitespace character on line: {self.line}, column: {self.column}"
            )
        if token_name == TokenNames.INDENTATION:
            number_of_tabs = token_value.count("\t")
            self.column += number_of_tabs
            if number_of_tabs > self.indent_level:
                for _ in range(number_of_tabs - self.indent_level):
                    self.add_new_token(TokenNames.INDENT, "indentation")
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
            self.add_new_token(TokenNames.DEDENT, "dedentation")
            self.indent_level -= 1

    def add_new_token(self, token_name, token_value):
        """Appends token_read attribute with new Token

        Args:
            token_name (str): new Token name
            token_value (str): new Token value
        """
        self.tokens_read.append(Token(token_name, token_value, self.line, self.column))
