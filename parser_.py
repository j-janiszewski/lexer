from scanner import Token, TokenNames, Scanner

VALID_PROPERTY_VALUES = [
    TokenNames.ID,
    TokenNames.HEX_VALUE,
    TokenNames.INT_VALUE,
    TokenNames.PX_VALUE,
    TokenNames.REM_VAlUE,
    TokenNames.TEXT_VALUE,
    TokenNames.URL_VALUE,
    TokenNames.PERC_VALUE,
]


class Parser:
    def __init__(self, scanner: Scanner):
        self.__tokens = scanner.tokens_read
        self.program_end = False
        self.parse_program()

    @property
    def current_token_name(self):
        return self.tokens[0].name

    def move_to_next_token(self, n=1):
        self.tokens = self.tokens[n:]

    @property
    def tokens(self):
        return self.__tokens

    @tokens.setter
    def tokens(self, new_tokens_value):
        if len(new_tokens_value) == 0 and not self.program_end:
            raise RuntimeError(
                f"Unexcpected end of file - error at line: {self.line_number}, column: {self.column_number}"
            )
        else:
            self.__tokens = new_tokens_value

    @property
    def line_number(self):
        return self.tokens[0].line

    @property
    def column_number(self):
        self.tokens[0].column

    def take_token(self, expected_token, additional_msg=None):
        if self.current_token_name != expected_token:
            print(self.current_token_name, self.tokens[0].value)
            if self.column_number:
                msg = f"Expected {expected_token} - error at line: {self.line_number}, column: {self.column_number}"
            else:
                msg = f"Expected {expected_token} - error at the beginning of line: {self.line_number}"
            if additional_msg:
                msg = f"{additional_msg} + {msg}"
            raise RuntimeError(msg)

        self.move_to_next_token()

    def take_value_token(self, additional_msg=None):
        if not self.current_token_name in VALID_PROPERTY_VALUES:
            msg = f"Expected property value - error at line: {self.line_number}, column: {self.column_number}"
            if additional_msg:
                msg = f"{additional_msg} + {msg}"
            raise RuntimeError(msg)
        taken_token = self.current_token_name
        self.move_to_next_token()
        return taken_token

    def parse_program(self):
        while len(self.tokens) != 0:
            if self.current_token_name == TokenNames.NEWLINE:
                self.move_to_next_token()
                continue
            elif self.current_token_name == TokenNames.EOL:
                self.program_end = True
                self.take_token(TokenNames.EOL)
            else:
                self.parse_entry()

    def parse_entry(self):
        self.parse_select()
        self.take_token(
            TokenNames.NEWLINE,
            additional_msg="After select block newline must be present",
        )
        self.take_token(
            TokenNames.INDENT,
            additional_msg="After select block indentation must be present",
        )
        self.parse_properties()
        self.take_token(TokenNames.DEDENT)
        while self.current_token_name == TokenNames.NEWLINE:
            self.take_token(TokenNames.NEWLINE)

    def parse_select(self):
        self.take_token(expected_token=TokenNames.ID)
        #  ID OPERATOR ID
        if self.current_token_name == TokenNames.OPERATOR:
            self.take_token(TokenNames.OPERATOR)
            self.take_token(TokenNames.ID)
        else:
            # LIST_OF_IDS
            while self.current_token_name == TokenNames.ID:
                self.take_token(TokenNames.ID)
        # SELECT COMMA NEWLINE SELECT
        if self.current_token_name == TokenNames.COMMA:
            self.take_token(TokenNames.COMMA)
            self.take_token(
                TokenNames.NEWLINE,
                additional_msg="New selector must be placed in new line",
            )
            self.parse_select()

    def parse_properties(self):
        no_semicolon = False
        while self.current_token_name != TokenNames.DEDENT and not no_semicolon:
            no_semicolon = self.parse_property()

    def parse_property(self):
        self.take_token(TokenNames.PROPERTY_NAME)
        value_type = self.take_value_token()
        # VALUE -> VALUE IMPORTANT
        if self.current_token_name == TokenNames.IMPORTANT:
            self.take_token(TokenNames.IMPORTANT)
        # VALUE -> PX_VALUE ID HEX_VALUE
        elif (
            value_type == TokenNames.PX_VALUE
            and self.current_token_name == TokenNames.ID
        ):
            self.take_token(TokenNames.ID)
            self.take_token(TokenNames.HEX_VALUE)

        if self.current_token_name == TokenNames.SEMICOLON:
            self.take_token(TokenNames.SEMICOLON)
            self.take_token(
                TokenNames.NEWLINE,
                additional_msg="After property newline must be present",
            )
            return False
        else:
            self.take_token(
                TokenNames.NEWLINE, "After property newline must be present"
            )
            return True
