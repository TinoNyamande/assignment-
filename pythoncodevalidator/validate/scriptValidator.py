from abc import ABC, abstractmethod
import re
python_keywords = [
    "False", "None", "True", "and", "as", "assert", "async", "await", "break",
    "class", "continue", "def", "del", "elif", "else", "except", "finally",
    "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
    "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"
]

def is_valid_identifier(identifier):
    pattern = r'^[a-zA-Z_]\w*$'
    return re.match(pattern, identifier) is not None

def extract_arguments(line):
    match = re.search(r'\(([^)]*)\)', line)
    
    if match:
        arguments_str = match.group(1).strip()
        
        if arguments_str:
            arguments = [arg.strip() for arg in arguments_str.split(',')]
            return arguments
        return []  
    return None 


class ScriptValidatorAbstract(ABC):
    @abstractmethod
    def identifierValidation(self, line, line_number):
        pass
    
    @abstractmethod
    def methodSignatureValidation(self, line, line_number):
        pass
    
    @abstractmethod
    def classSignatureValidation(self, line, line_number):
        pass
    
    @abstractmethod
    def indentationValidation(self, line, line_number):
        pass

    @abstractmethod
    def loopsValidation(self,line,line_number):
        pass

expect_indent_for_next_line = False
expect_indent_for_current_line = False

class ScriptValidator(ScriptValidatorAbstract):
    def __init__(self, indentation_size=4):
        self.indentation_size = indentation_size
        self.indentation_stack = [0]
        self.errors = []

    def indentationValidation(self, line, line_number):
        global expect_indent_for_next_line, expect_indent_for_current_line
        #if in previos iteration expect_indent_for_next_line was set to true.
        #expect indent _for current _line should be set to true as well 
        #otherwise false indication current line should be on the same level as previous line
        expect_indent_for_current_line = expect_indent_for_next_line
       
       #calculate the current indentation by subtracting striped line from unstriped line
        stripped_line = line.lstrip()
        current_indentation = len(line) - len(stripped_line)
       
        #ignore if the current line is empty or i a comment
        if not stripped_line or stripped_line.startswith('#') or stripped_line.startswith("'''") or stripped_line.startswith('"""') or stripped_line.startswith("'") or stripped_line.startswith('"')  or stripped_line.startswith('}') or stripped_line.startswith(')'):
            expect_indent_for_current_line = False
            return
        
        #if inentationis expcted but none is found
        if expect_indent_for_current_line:
            if current_indentation <= self.indentation_stack[-1]:
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Expected indentation at line {line_number}.'
                })
            expect_indent_for_next_line = False  
        # if a line ends with a colon  indentation should be expected oin the next line
        if stripped_line.rstrip().endswith(':') and not stripped_line.startswith('#'):
            print("Indent expected")
            expect_indent_for_next_line = True  
        
        #if no indentation is found but the line is indented
        if not expect_indent_for_current_line and current_indentation > self.indentation_stack[-1]:
            print("Unexpected Indentation")
            print("Indentation Stack:", self.indentation_stack[-1])
            self.errors.append({
                'lineNumber': line_number,
                'message': f'Unexpected indentation at line {line_number}.'
            })
        
         #Checks if the current indentation level :current_indentation
        # is greater than the last indentation level stored in the stack 
       # If true, this means the code is starting a new block e.g inside a function or a loop
        # so it appends the new indentation level to the stack. 
        if current_indentation > self.indentation_stack[-1]:
            self.indentation_stack.append(current_indentation)
        # this indicates that the code is ending a block and returning to a previous indentation level. 
        # The while loop removes  levels from the stack until the stack's top level is less than or equal 
        # to the current indentation.
       
        elif current_indentation < self.indentation_stack[-1]:
            while self.indentation_stack and current_indentation < self.indentation_stack[-1]:
                self.indentation_stack.pop()

    def identifierValidation(self, line, line_number):
        #regex to find assinged variables
        match = re.match(r'\b([a-zA-Z_]\w*)\s*=\s*.*', line)
        
        if match:
            identifier = match.group(1)
            #check if identifer name is a keyword
            if identifier in python_keywords:
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid identifier "{identifier}" at line {line_number}. Keywords cannot be used as identifiers.'
                })
            #validate identifer name against helper function
            elif not is_valid_identifier(identifier):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid identifier "{identifier}" at line {line_number}. Identifiers should start with letters or underscores and contain only alphanumeric characters and underscores.'
                })

#  methiod for validatinfg function declaration
    def methodSignatureValidation(self, line, line_number):
        stripped_line = line.strip()
        #check if line starts with def else return
        if stripped_line.startswith('def '):
            #check if line matches correct method signature
            #^def : line should start with def
            #\s+ at least one occurence of any empty space
            #[a-zA-Z_] function name should start with letters or underscore
            #\w* followed by 0 or more occurences of any characters
            #\s* zero or more occurences of empty space
            #(.*\) parenthesis with zero or more characters (arguments)
            #\s* zero or more occurences of empty space
            # :$ line should end with colon
            pattern = r'^def\s+[a-zA-Z_]\w*\s*\(.*\)\s*:$'
            if not re.match(pattern, stripped_line):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid method signature at line {line_number}.'
                })
            # retrieve the method name and check if it is contained in keywords and
            #follows naming conventions
            match = re.match(r'^\s*def\s+([a-zA-Z_]\w*)\s*\(', line)
            methodName = match.group(1);
            if methodName in python_keywords:
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid method name: {methodName}. Method name cannot be a keyword'
                })
            elif not is_valid_identifier(methodName):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid identifier {methodName} .Method name should start with letters or underscores and contain only alphanumeric characters and underscores.'
                })
            elif not methodName:
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'no name provided for function .'
                })
            #retrieve the arguments string and ensure the arguments are comma seperated
            argsMatch = re.search(r'\(([^)]*)\)', line)
            if argsMatch:
                arguments_str = match.group(1).strip()
                if arguments_str.startswith(',') or arguments_str.endswith(','):
                    self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid arguments passed to function: {arguments_str}'
                     })
                invalid_pattern = r'\b[a-zA-Z_]\w*\s+[a-zA-Z_]\w*\b'
                if re.search(invalid_pattern,arguments_str):
                    self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid arguments passed to function: "{arguments_str}".Arguments should be seperated by commas'
                    })
            #retrieve each argument and checjk if it follows identfier naming conventions
            args = extract_arguments(line)
            if args:
                for arg in args:
                    if arg in python_keywords:
                       self.errors.append({
                       'lineNumber': line_number,
                       'message': f'Keyword {arg} cannot be used as argument'
                       })
                    elif not is_valid_identifier(arg):
                        self.errors.append({
                       'lineNumber': line_number,
                       'message': f'Invalid argument: "{arg}" passed to function.'
                       })
            
                

    def classSignatureValidation(self, line, line_number):
        stripped_line = line.strip()

        pattern = r'^class\s+[a-zA-Z_]\w*(\s*\(.*\))?\s*:\s*$'
        if stripped_line.startswith('class '): 
            if not re.match(pattern, stripped_line):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid class signature at line {line_number}.'
                })
           # retrieve the class name and check if it is contained in keywords and
            #follows naming conventions
            match = re.match(r'^\s*class\s+([a-zA-Z_]\w*)\s*\(', line)
            if match:
                className = match.group(1);
                if className in python_keywords:
                    self.errors.append({
                        'lineNumber': line_number,
                        'message': f'Invalid method name: {className}. Method name cannot be a keyword'
                    })
                elif not is_valid_identifier(className):
                    self.errors.append({
                         'lineNumber': line_number,
                        'message': f'Invalid identifier {className} .Method name should start with letters or underscores and contain only alphanumeric characters and underscores.'
                    })

            else : 
                self.errors.append({
                     'lineNumber': line_number,
                        'message': f'no name provided for class .'
                    })

            #retrieve the arguments string and ensure the arguments are comma seperated
            argsMatch = re.search(r'\(([^)]*)\)', line)
            print(f'Args {argsMatch}')
            if argsMatch:
                arguments_str = match.group(1).strip()
                if arguments_str.startswith(',') or arguments_str.endswith(','):
                    self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid arguments passed to function: {arguments_str}'
                     })
                invalid_pattern = r'\b[a-zA-Z_]\w*\s+[a-zA-Z_]\w*\b'
                if re.search(invalid_pattern,arguments_str):
                    self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid arguments passed to function: "{arguments_str}".Arguments should be seperated by commas'
                    })
            #retrieve each argument and checjk if it follows identfier naming conventions
            args = extract_arguments(line)
            if args:
                for arg in args:
                    if arg in python_keywords:
                       self.errors.append({
                       'lineNumber': line_number,
                       'message': f'Keyword {arg} cannot be used as argument'
                       })
                    elif not is_valid_identifier(arg):
                        self.errors.append({
                       'lineNumber': line_number,
                       'message': f'Invalid argument: "{arg}" passed to function.'
                       })
     
    def loopsValidation(self,line,line_number) :
        stripped_line = line.strip()
        if stripped_line.startswith('if ') or  stripped_line.startswith('elif ') or  stripped_line.startswith('else if '):
            if not stripped_line.endswith(":"):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Expected : at the end of statement'
                })
            if_pattern = r'^(if|elif|elseif)\s+.*\s*:'

            if not re.match(if_pattern, stripped_line):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid  loop syntax for if/elif statement .'
                })
        if stripped_line.startswith('while '):
            if not stripped_line.endswith(":"):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Expected : at the end of statement'
                })
            while_pattern = r'^while\s+.*\s*:$'
            if not re.match(while_pattern, stripped_line):
                    self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid "while" loop syntax.'
                })
        if stripped_line.startswith('for '):
            if not stripped_line.endswith(":"):
                self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Expected : at the end of statement'
                })
            for_pattern = r'^for\s+[a-zA-Z_]\w*\s+in\s+.*\s*:$' 

            if not re.match(for_pattern, stripped_line):
                    self.errors.append({
                    'lineNumber': line_number,
                    'message': f'Invalid "for" loop syntax.'
                })

    def validate(self, file):
        global expect_indent_for_next_line, expect_indent_for_current_line  
        expect_indent_for_next_line = False
        expect_indent_for_current_line = False
        file.seek(0)
        lines = file.read().decode('utf-8').splitlines()
        for i, line in enumerate(lines, start=1):
            self.indentationValidation(line,i)
            self.classSignatureValidation(line,i)
            self.methodSignatureValidation(line, i)
            self.identifierValidation(line,i)
            self.loopsValidation(line,i)
        return self.errors
