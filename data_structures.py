"""
Data Structures for SIC/XE Assembler
Contains: OPTAB, SYMTAB, LITTAB, Instruction class

Team: Ilyas, Nadja
"""


class Instruction:
    """Represents a single line of assembly code"""
    
    def __init__(self, line_num=0, line=""):
        self.line_num = line_num
        self.original_line = line
        self.address = 0
        self.label = ""
        self.mnemonic = ""
        self.operand = ""
        self.comment = ""
        self.is_comment = False
        self.is_directive = False
        self.format = 0
        self.object_code = ""
        self.error = ""
        
    def __repr__(self):
        return f"Instruction({self.line_num}, {self.label}, {self.mnemonic}, {self.operand})"


class OPTAB:
    """Operation Code Table - stores instruction information"""
    
    def __init__(self):
        # Format: mnemonic: (opcode, format)
        self.table = {
            # Format 3/4 instructions
            'ADD': (0x18, 3),
            'ADDF': (0x58, 3),
            'ADDR': (0x90, 2),
            'AND': (0x40, 3),
            'CLEAR': (0xB4, 2),
            'COMP': (0x28, 3),
            'COMPF': (0x88, 3),
            'COMPR': (0xA0, 2),
            'DIV': (0x24, 3),
            'DIVF': (0x64, 3),
            'DIVR': (0x9C, 2),
            'FIX': (0xC4, 1),
            'FLOAT': (0xC0, 1),
            'HIO': (0xF4, 1),
            'J': (0x3C, 3),
            'JEQ': (0x30, 3),
            'JGT': (0x34, 3),
            'JLT': (0x38, 3),
            'JSUB': (0x48, 3),
            'LDA': (0x00, 3),
            'LDB': (0x68, 3),
            'LDCH': (0x50, 3),
            'LDF': (0x70, 3),
            'LDL': (0x08, 3),
            'LDS': (0x6C, 3),
            'LDT': (0x74, 3),
            'LDX': (0x04, 3),
            'LPS': (0xD0, 3),
            'MUL': (0x20, 3),
            'MULF': (0x60, 3),
            'MULR': (0x98, 2),
            'NORM': (0xC8, 1),
            'OR': (0x44, 3),
            'RD': (0xD8, 3),
            'RMO': (0xAC, 2),
            'RSUB': (0x4C, 3),
            'SHIFTL': (0xA4, 2),
            'SHIFTR': (0xA8, 2),
            'SIO': (0xF0, 1),
            'SSK': (0xEC, 3),
            'STA': (0x0C, 3),
            'STB': (0x78, 3),
            'STCH': (0x54, 3),
            'STF': (0x80, 3),
            'STI': (0xD4, 3),
            'STL': (0x14, 3),
            'STS': (0x7C, 3),
            'STSW': (0xE8, 3),
            'STT': (0x84, 3),
            'STX': (0x10, 3),
            'SUB': (0x1C, 3),
            'SUBF': (0x5C, 3),
            'SUBR': (0x94, 2),
            'SVC': (0xB0, 2),
            'TD': (0xE0, 3),
            'TIO': (0xF8, 1),
            'TIX': (0x2C, 3),
            'TIXR': (0xB8, 2),
            'WD': (0xDC, 3),
        }
        
        # Directives
        self.directives = {
            'START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW',
            'BASE', 'NOBASE', 'LTORG', 'EQU', 'ORG', 'USE'
        }
        
    def get_opcode(self, mnemonic):
        """Get opcode for a mnemonic"""
        # Remove + prefix for Format 4
        clean_mnemonic = mnemonic.lstrip('+')
        if clean_mnemonic in self.table:
            return self.table[clean_mnemonic][0]
        return None
        
    def get_format(self, mnemonic):
        """Get format for a mnemonic"""
        # Handle Format 4 (+ prefix)
        if mnemonic.startswith('+'):
            return 4
        clean_mnemonic = mnemonic.lstrip('+')
        if clean_mnemonic in self.table:
            return self.table[clean_mnemonic][1]
        return 0
        
    def is_valid_instruction(self, mnemonic):
        """Check if mnemonic is valid"""
        clean_mnemonic = mnemonic.lstrip('+')
        return clean_mnemonic in self.table
        
    def is_directive(self, mnemonic):
        """Check if mnemonic is a directive"""
        return mnemonic.upper() in self.directives


class SYMTAB:
    """Symbol Table - stores labels and their addresses"""
    
    def __init__(self):
        self.symbols = {}
        
    def add_symbol(self, label, address):
        """Add a symbol to the table"""
        if label in self.symbols:
            return False  # Duplicate symbol
        self.symbols[label] = address
        return True
        
    def get_address(self, symbol):
        """Get address of a symbol"""
        return self.symbols.get(symbol, None)
        
    def exists(self, symbol):
        """Check if symbol exists"""
        return symbol in self.symbols
        
    def __len__(self):
        return len(self.symbols)
        
    def __repr__(self):
        return f"SYMTAB({len(self.symbols)} symbols)"


class LITTAB:
    """Literal Table - stores literals and their addresses"""
    
    def __init__(self):
        # Format: {literal_string: {'value': int, 'address': int, 'length': int}}
        self.literals = {}
        self.pending_literals = []  # Literals not yet assigned addresses
        
    def add_literal(self, literal):
        """Add a literal (without address initially)"""
        if literal not in self.literals:
            value, length = self._parse_literal(literal)
            self.literals[literal] = {
                'value': value,
                'address': None,
                'length': length
            }
            self.pending_literals.append(literal)
            
    def assign_address(self, literal, address):
        """Assign address to a literal"""
        if literal in self.literals:
            self.literals[literal]['address'] = address
            if literal in self.pending_literals:
                self.pending_literals.remove(literal)
                
    def get_address(self, literal):
        """Get address of a literal"""
        if literal in self.literals:
            return self.literals[literal]['address']
        return None
        
    def get_value(self, literal):
        """Get value of a literal"""
        if literal in self.literals:
            return self.literals[literal]['value']
        return None
        
    def get_length(self, literal):
        """Get length of a literal"""
        if literal in self.literals:
            return self.literals[literal]['length']
        return 0
        
    def has_pending(self):
        """Check if there are pending literals"""
        return len(self.pending_literals) > 0
        
    def get_pending(self):
        """Get list of pending literals"""
        return self.pending_literals.copy()
        
    def _parse_literal(self, literal):
        """Parse literal to get value and length"""
        # Remove leading =
        literal = literal[1:]
        
        if literal.startswith('C'):
            # Character literal: =C'EOF'
            content = literal[2:-1]  # Remove C' and '
            value = 0
            for char in content:
                value = (value << 8) | ord(char)
            return value, len(content)
            
        elif literal.startswith('X'):
            # Hex literal: =X'05'
            content = literal[2:-1]  # Remove X' and '
            value = int(content, 16)
            length = (len(content) + 1) // 2  # 2 hex digits = 1 byte
            return value, length
            
        else:
            # Assume decimal
            value = int(literal)
            return value, 3
            
    def __len__(self):
        return len(self.literals)
        
    def __repr__(self):
        return f"LITTAB({len(self.literals)} literals)"


# Register codes for Format 2 instructions
REGISTERS = {
    'A': 0,
    'X': 1,
    'L': 2,
    'B': 3,
    'S': 4,
    'T': 5,
    'F': 6,
    'PC': 8,
    'SW': 9
}


def get_register_code(register):
    """Get numeric code for a register"""
    return REGISTERS.get(register.upper(), None)