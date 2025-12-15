"""
Input Processor for SIC/XE Assembler
Reads source file and parses instructions

Team: Ilyas, Nadja (Shared)
"""

import re
from data_structures import Instruction


class InputProcessor:
    """Handles reading and parsing of assembly source files"""
    
    def __init__(self):
        self.errors = []
        
    def read_source_file(self, filename):
        """Read source file and return list of Instruction objects"""
        instructions = []
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, start=1):
                instr = self.parse_line(line, line_num)
                instructions.append(instr)
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Source file '{filename}' not found")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
            
        return instructions
        
    def parse_line(self, line, line_num):
        """Parse a single line into an Instruction object"""
        instr = Instruction(line_num, line.rstrip('\n'))
        
        # Remove trailing newline and handle empty lines
        line = line.rstrip('\n')
        
        if not line or line.strip() == '':
            instr.is_comment = True
            return instr
            
        # Check for comment line (starts with .)
        if line.strip().startswith('.'):
            instr.is_comment = True
            instr.comment = line.strip()
            return instr
            
        # Split line into components
        # Format: [LABEL] MNEMONIC [OPERAND] [COMMENT]
        
        # Check for inline comment
        if '.' in line:
            # Split at first . that's not part of a string
            parts = line.split('.', 1)
            line = parts[0]
            instr.comment = '.' + parts[1]
            
        line = line.rstrip()
        
        # Tokenize the line
        label, mnemonic, operand = self._tokenize(line)
        
        instr.label = label
        instr.mnemonic = mnemonic
        instr.operand = operand
        
        return instr
        
    def _tokenize(self, line):
        """Split line into label, mnemonic, operand"""
        # SIC/XE format:
        # - Label starts in column 1 (no whitespace before it)
        # - If line starts with whitespace, no label
        # - Mnemonic follows label (or starts line if no label)
        # - Operand follows mnemonic
        
        label = ""
        mnemonic = ""
        operand = ""
        
        # Check if line starts with whitespace
        if line and line[0] in ' \t':
            # No label
            parts = line.strip().split(None, 1)  # Split on whitespace
            if len(parts) >= 1:
                mnemonic = parts[0]
            if len(parts) >= 2:
                operand = parts[1].strip()
        else:
            # Has label
            parts = line.split(None, 2)  # Split into 3 parts max
            if len(parts) >= 1:
                label = parts[0]
            if len(parts) >= 2:
                mnemonic = parts[1]
            if len(parts) >= 3:
                operand = parts[2].strip()
                
        return label, mnemonic.upper(), operand
        
    def validate_label(self, label):
        """Validate label format"""
        if not label:
            return True  # Empty label is ok
            
        # Label rules:
        # - Max 6 characters
        # - Must start with letter
        # - Can contain letters and digits
        
        if len(label) > 6:
            return False
            
        if not label[0].isalpha():
            return False
            
        if not label.isalnum():
            return False
            
        return True
        
    def validate_syntax(self, instruction):
        """Basic syntax validation"""
        # Check label
        if not self.validate_label(instruction.label):
            return False, f"Invalid label: {instruction.label}"
            
        # Check mnemonic is not empty
        if not instruction.mnemonic and not instruction.is_comment:
            return False, "Missing mnemonic"
            
        return True, "OK"


def test_input_processor():
    """Test function for InputProcessor"""
    print("Testing InputProcessor...")
    
    # Create test file
    test_code = """COPY    START   1000
FIRST   LDA     ALPHA
        STA     BETA        . Store value
ALPHA   RESW    1
BETA    RESW    1
        END     FIRST
"""
    
    with open('test_input.asm', 'w') as f:
        f.write(test_code)
        
    # Test reading
    processor = InputProcessor()
    instructions = processor.read_source_file('test_input.asm')
    
    print(f"\nRead {len(instructions)} lines:")
    for instr in instructions:
        if not instr.is_comment:
            print(f"  Line {instr.line_num}: "
                  f"'{instr.label}' '{instr.mnemonic}' '{instr.operand}'")
                  
    import os
    os.remove('test_input.asm')
    print("\n✓ InputProcessor test passed")


if __name__ == '__main__':
    test_input_processor()