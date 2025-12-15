"""
Pass 1 of SIC/XE Assembler
Builds symbol table and calculates addresses

Team: Ilyas
"""

from data_structures import SYMTAB, LITTAB


class Pass1Assembler:
    """Pass 1: Build symbol table and assign addresses"""
    
    def __init__(self, instructions, optab):
        self.instructions = instructions
        self.optab = optab
        self.symtab = SYMTAB()
        self.littab = LITTAB()
        self.locctr = 0
        self.start_address = 0
        self.program_name = ""
        self.program_length = 0
        self.errors = []
        self.base_register = 0
        
    def process(self):
        """Execute Pass 1"""
        # Find START directive
        start_found = False
        
        for i, instr in enumerate(self.instructions):
            if instr.is_comment:
                continue
                
            if instr.mnemonic == 'START':
                start_found = True
                self.program_name = instr.label
                self.start_address = int(instr.operand, 16) if instr.operand else 0
                self.locctr = self.start_address
                instr.address = self.locctr
                continue
                
            break
            
        if not start_found:
            self.locctr = 0
            self.start_address = 0
            
        # Process each instruction
        for instr in self.instructions:
            if instr.is_comment:
                continue
                
            if instr.mnemonic == 'START':
                continue
                
            if instr.mnemonic == 'END':
                # Assign addresses to pending literals
                self._process_literals()
                instr.address = self.locctr
                break
                
            # Set address for this instruction
            instr.address = self.locctr
            
            # Process label
            if instr.label:
                if not self.symtab.add_symbol(instr.label, self.locctr):
                    self.errors.append(
                        f"Line {instr.line_num}: Duplicate symbol '{instr.label}'"
                    )
                    
            # Check for literal in operand
            if instr.operand and instr.operand.startswith('='):
                self.littab.add_literal(instr.operand)
                
            # Process instruction/directive
            if self.optab.is_directive(instr.mnemonic):
                self._process_directive(instr)
            else:
                self._process_instruction(instr)
                
        # Calculate program length
        self.program_length = self.locctr - self.start_address
        
        return self.symtab, self.littab, self.program_length
        
    def _process_instruction(self, instr):
        """Process a machine instruction"""
        # Determine format
        format_num = self.optab.get_format(instr.mnemonic)
        
        if format_num == 0:
            self.errors.append(
                f"Line {instr.line_num}: Invalid mnemonic '{instr.mnemonic}'"
            )
            return
            
        instr.format = format_num
        instr.is_directive = False
        
        # Increment LOCCTR by instruction size
        self.locctr += format_num
        
    def _process_directive(self, instr):
        """Process an assembler directive"""
        instr.is_directive = True
        mnemonic = instr.mnemonic
        operand = instr.operand
        
        if mnemonic == 'RESW':
            # Reserve words
            words = int(operand) if operand else 0
            self.locctr += 3 * words
            
        elif mnemonic == 'RESB':
            # Reserve bytes
            bytes_count = int(operand) if operand else 0
            self.locctr += bytes_count
            
        elif mnemonic == 'WORD':
            # One word constant
            self.locctr += 3
            
        elif mnemonic == 'BYTE':
            # Byte constant
            length = self._calculate_byte_length(operand)
            self.locctr += length
            
        elif mnemonic == 'BASE':
            # BASE directive (no space allocation)
            pass
            
        elif mnemonic == 'NOBASE':
            # NOBASE directive (no space allocation)
            pass
            
        elif mnemonic == 'LTORG':
            # Process pending literals
            self._process_literals()
            
        elif mnemonic == 'EQU':
            # EQU directive - assign value to symbol
            if instr.label:
                if operand == '*':
                    value = self.locctr
                else:
                    try:
                        value = int(operand, 16)
                    except:
                        value = self.locctr
                        
                if not self.symtab.add_symbol(instr.label, value):
                    self.errors.append(
                        f"Line {instr.line_num}: Duplicate symbol '{instr.label}'"
                    )
                    
        elif mnemonic == 'ORG':
            # ORG directive - change LOCCTR
            if operand:
                if operand == '*':
                    pass  # No change
                else:
                    try:
                        self.locctr = int(operand, 16)
                    except:
                        pass
                        
    def _calculate_byte_length(self, operand):
        """Calculate length of BYTE directive"""
        if not operand:
            return 0
            
        if operand.startswith("C'"):
            # Character constant: C'EOF' = 3 bytes
            content = operand[2:-1]  # Remove C' and '
            return len(content)
            
        elif operand.startswith("X'"):
            # Hex constant: X'05' = 1 byte (2 hex digits = 1 byte)
            content = operand[2:-1]  # Remove X' and '
            return (len(content) + 1) // 2
            
        return 1
        
    def _process_literals(self):
        """Assign addresses to pending literals"""
        pending = self.littab.get_pending()
        
        for literal in pending:
            self.littab.assign_address(literal, self.locctr)
            length = self.littab.get_length(literal)
            self.locctr += length


def test_pass1():
    """Test function for Pass 1"""
    print("Testing Pass 1...")
    
    from data_structures import Instruction, OPTAB
    
    # Create test instructions
    instructions = [
        Instruction(1, "COPY    START   1000"),
        Instruction(2, "FIRST   LDA     ALPHA"),
        Instruction(3, "        STA     BETA"),
        Instruction(4, "ALPHA   RESW    1"),
        Instruction(5, "BETA    RESW    1"),
        Instruction(6, "        END     FIRST"),
    ]
    
    # Parse them
    from input_processor import InputProcessor
    processor = InputProcessor()
    
    for instr in instructions:
        label, mnemonic, operand = processor._tokenize(instr.original_line)
        instr.label = label
        instr.mnemonic = mnemonic
        instr.operand = operand
        
    # Run Pass 1
    optab = OPTAB()
    pass1 = Pass1Assembler(instructions, optab)
    symtab, littab, length = pass1.process()
    
    print(f"\nProgram Length: {length:04X}")
    print(f"\nSymbol Table ({len(symtab)} symbols):")
    for symbol, addr in sorted(symtab.symbols.items()):
        print(f"  {symbol:8s} {addr:04X}")
        
    if pass1.errors:
        print("\nErrors:")
        for error in pass1.errors:
            print(f"  {error}")
    else:
        print("\n✓ Pass 1 test passed")


if __name__ == '__main__':
    test_pass1()