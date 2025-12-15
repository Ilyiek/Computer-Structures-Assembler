"""
Pass 2 of SIC/XE Assembler
Generates object code

Team: Nadja
"""

from data_structures import get_register_code


class Pass2Assembler:
    """Pass 2: Generate object code"""
    
    def __init__(self, instructions, symtab, littab, optab):
        self.instructions = instructions
        self.symtab = symtab
        self.littab = littab
        self.optab = optab
        self.errors = []
        self.base_register = 0
        self.modification_records = []
        
    def process(self):
        """Execute Pass 2"""
        for instr in self.instructions:
            if instr.is_comment or instr.mnemonic in ['START', 'END']:
                continue
                
            # Handle BASE directive
            if instr.mnemonic == 'BASE':
                if instr.operand:
                    if self.symtab.exists(instr.operand):
                        self.base_register = self.symtab.get_address(instr.operand)
                    else:
                        try:
                            self.base_register = int(instr.operand, 16)
                        except:
                            pass
                continue
                
            if instr.mnemonic == 'NOBASE':
                self.base_register = 0
                continue
                
            # Generate object code for instructions
            if not instr.is_directive:
                self._generate_instruction_code(instr)
            else:
                self._generate_directive_code(instr)
                
        return self.instructions
        
    def _generate_instruction_code(self, instr):
        """Generate object code for an instruction"""
        opcode = self.optab.get_opcode(instr.mnemonic)
        
        if opcode is None:
            self.errors.append(
                f"Line {instr.line_num}: Invalid opcode '{instr.mnemonic}'"
            )
            return
            
        format_num = instr.format
        
        if format_num == 1:
            # Format 1: just opcode (8 bits)
            instr.object_code = f"{opcode:02X}"
            
        elif format_num == 2:
            # Format 2: opcode + registers (16 bits)
            self._generate_format2(instr, opcode)
            
        elif format_num in [3, 4]:
            # Format 3/4: opcode + nixbpe + address/displacement
            self._generate_format34(instr, opcode, format_num)
            
    def _generate_format2(self, instr, opcode):
        """Generate Format 2 object code"""
        operands = instr.operand.split(',')
        
        r1 = 0
        r2 = 0
        
        if len(operands) >= 1 and operands[0]:
            r1_code = get_register_code(operands[0].strip())
            if r1_code is not None:
                r1 = r1_code
                
        if len(operands) >= 2:
            r2_code = get_register_code(operands[1].strip())
            if r2_code is not None:
                r2 = r2_code
                
        instr.object_code = f"{opcode:02X}{r1:01X}{r2:01X}"
        
    def _generate_format34(self, instr, opcode, format_num):
        """Generate Format 3/4 object code"""
        # Determine addressing mode flags
        ni = self._get_ni_flags(instr.operand)
        x = 1 if ',X' in instr.operand.upper() else 0
        
        # Get target address
        target_address = self._resolve_address(instr)
        
        if target_address is None:
            self.errors.append(
                f"Line {instr.line_num}: Undefined symbol in '{instr.operand}'"
            )
            instr.object_code = "ERROR"
            return
            
        if format_num == 4:
            # Format 4: e=1, b=0, p=0, 20-bit address
            b = 0
            p = 0
            e = 1
            
            nixbpe = (ni << 4) | (x << 3) | (b << 2) | (p << 1) | e
            
            # Combine: opcode(6) + ni(2) + x(1) + b(1) + p(1) + e(1) + address(20)
            first_byte = opcode + (ni >> 2)  # opcode + n bit
            second_byte = ((ni & 0x03) << 6) | (nixbpe & 0x3F)
            
            instr.object_code = f"{first_byte:02X}{second_byte:02X}{target_address:05X}"
            
            # Add modification record for Format 4
            self.modification_records.append({
                'address': instr.address + 1,
                'length': 5
            })
            
        else:
            # Format 3: calculate displacement
            pc = instr.address + 3  # PC points to next instruction
            
            # Try PC-relative first
            disp = target_address - pc
            
            if -2048 <= disp <= 2047:
                # PC-relative
                b = 0
                p = 1
                e = 0
                disp = disp & 0xFFF  # 12-bit two's complement
                
            elif self.base_register != 0:
                # Try base-relative
                disp = target_address - self.base_register
                
                if 0 <= disp <= 4095:
                    b = 1
                    p = 0
                    e = 0
                else:
                    self.errors.append(
                        f"Line {instr.line_num}: Displacement out of range"
                    )
                    instr.object_code = "ERROR"
                    return
            else:
                self.errors.append(
                    f"Line {instr.line_num}: Displacement out of range (no base register)"
                )
                instr.object_code = "ERROR"
                return
                
            nixbpe = (ni << 4) | (x << 3) | (b << 2) | (p << 1) | e
            
            # Combine: opcode(6) + nixbpe(6) + disp(12)
            first_byte = opcode + (ni >> 2)
            second_byte = ((ni & 0x03) << 6) | (nixbpe & 0x3F)
            
            instr.object_code = f"{first_byte:02X}{second_byte:02X}{disp:03X}"
            
    def _get_ni_flags(self, operand):
        """Determine n and i flags from operand"""
        if not operand:
            return 0b11  # Simple addressing (ni = 11)
            
        # Remove ,X for checking
        operand_clean = operand.split(',')[0].strip()
        
        if operand_clean.startswith('#'):
            # Immediate addressing (ni = 01)
            return 0b01
        elif operand_clean.startswith('@'):
            # Indirect addressing (ni = 10)
            return 0b10
        else:
            # Simple addressing (ni = 11)
            return 0b11
            
    def _resolve_address(self, instr):
        """Resolve operand to target address"""
        operand = instr.operand
        
        if not operand:
            return 0
            
        # Remove addressing mode prefixes and indexed suffix
        operand_clean = operand.replace('#', '').replace('@', '')
        operand_clean = operand_clean.split(',')[0].strip()
        
        # Check if literal
        if operand_clean.startswith('='):
            return self.littab.get_address(operand_clean)
            
        # Check if immediate value (numeric)
        if operand.startswith('#'):
            try:
                # Try to parse as number
                if operand_clean.isdigit():
                    return int(operand_clean)
                else:
                    # It's a symbol
                    return self.symtab.get_address(operand_clean)
            except:
                return self.symtab.get_address(operand_clean)
                
        # It's a symbol
        return self.symtab.get_address(operand_clean)
        
    def _generate_directive_code(self, instr):
        """Generate object code for directives that produce data"""
        if instr.mnemonic == 'WORD':
            # Generate 3-byte word
            try:
                value = int(instr.operand)
                if value < 0:
                    value = (1 << 24) + value  # Two's complement
                instr.object_code = f"{value:06X}"
            except:
                instr.object_code = "000000"
                
        elif instr.mnemonic == 'BYTE':
            # Generate byte constant
            instr.object_code = self._generate_byte_code(instr.operand)
            
    def _generate_byte_code(self, operand):
        """Generate object code for BYTE directive"""
        if operand.startswith("C'"):
            # Character constant
            content = operand[2:-1]
            result = ""
            for char in content:
                result += f"{ord(char):02X}"
            return result
            
        elif operand.startswith("X'"):
            # Hex constant
            content = operand[2:-1]
            return content
            
        return ""


def test_pass2():
    """Test function for Pass 2"""
    print("Testing Pass 2...")
    
    from data_structures import Instruction, OPTAB, SYMTAB, LITTAB
    from input_processor import InputProcessor
    
    # Create test instructions with addresses from Pass 1
    test_lines = [
        "COPY    START   1000",
        "FIRST   LDA     ALPHA",
        "        STA     BETA",
        "ALPHA   WORD    5",
        "BETA    RESW    1",
        "        END     FIRST",
    ]
    
    instructions = []
    processor = InputProcessor()
    
    for i, line in enumerate(test_lines, 1):
        instr = processor.parse_line(line, i)
        instructions.append(instr)
        
    # Simulate Pass 1 results
    instructions[0].address = 0x1000
    instructions[1].address = 0x1000
    instructions[1].format = 3
    instructions[2].address = 0x1003
    instructions[2].format = 3
    instructions[3].address = 0x1006
    instructions[4].address = 0x1009
    
    symtab = SYMTAB()
    symtab.add_symbol('FIRST', 0x1000)
    symtab.add_symbol('ALPHA', 0x1006)
    symtab.add_symbol('BETA', 0x1009)
    
    littab = LITTAB()
    optab = OPTAB()
    
    # Run Pass 2
    pass2 = Pass2Assembler(instructions, symtab, littab, optab)
    pass2.process()
    
    print("\nObject Code Generated:")
    for instr in instructions:
        if instr.object_code:
            print(f"  {instr.address:04X}  {instr.object_code:8s}  "
                  f"{instr.mnemonic}")
                  
    if pass2.errors:
        print("\nErrors:")
        for error in pass2.errors:
            print(f"  {error}")
    else:
        print("\n✓ Pass 2 test passed")


if __name__ == '__main__':
    test_pass2()