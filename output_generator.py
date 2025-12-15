"""
Output Generator for SIC/XE Assembler
Generates object program file

Team: Nadja
"""


class OutputGenerator:
    """Generates object program in standard format"""
    
    def __init__(self):
        self.records = []
        
    def write_object_file(self, filename, instructions, symtab, pass2_obj):
        """Write complete object file"""
        try:
            with open(filename, 'w') as f:
                # Generate Header record
                header = self._generate_header(instructions)
                f.write(header + '\n')
                
                # Generate Text records
                text_records = self._generate_text_records(instructions)
                for record in text_records:
                    f.write(record + '\n')
                    
                # Generate Modification records
                mod_records = self._generate_modification_records(pass2_obj)
                for record in mod_records:
                    f.write(record + '\n')
                    
                # Generate End record
                end_record = self._generate_end_record(instructions)
                f.write(end_record + '\n')
                
            return True
            
        except Exception as e:
            print(f"Error writing object file: {e}")
            return False
            
    def _generate_header(self, instructions):
        """Generate Header record: H^name^start_addr^length"""
        program_name = ""
        start_addr = 0
        program_length = 0
        
        # Find START directive
        for instr in instructions:
            if instr.mnemonic == 'START':
                program_name = instr.label if instr.label else "PROG"
                start_addr = instr.address
                break
                
        # Find program length
        for instr in reversed(instructions):
            if instr.mnemonic == 'END':
                # Length is from start to last address
                for i in reversed(instructions):
                    if i.object_code and i.object_code != "ERROR":
                        program_length = (i.address - start_addr) + (len(i.object_code) // 2)
                        break
                break
                
        # Format: H^name(6)^start(6)^length(6)
        name = f"{program_name:<6s}"[:6]
        return f"H^{name}^{start_addr:06X}^{program_length:06X}"
        
    def _generate_text_records(self, instructions):
        """Generate Text records: T^start^length^object_codes"""
        text_records = []
        current_record = {
            'start': None,
            'codes': []
        }
        
        MAX_LENGTH = 60  # Max 60 hex chars (30 bytes)
        
        for instr in instructions:
            if not instr.object_code or instr.object_code == "ERROR":
                # Flush current record if any
                if current_record['codes']:
                    text_records.append(self._format_text_record(current_record))
                    current_record = {'start': None, 'codes': []}
                continue
                
            # Skip directives that don't produce code
            if instr.is_directive and instr.mnemonic in ['RESW', 'RESB']:
                if current_record['codes']:
                    text_records.append(self._format_text_record(current_record))
                    current_record = {'start': None, 'codes': []}
                continue
                
            # Start new record if needed
            if current_record['start'] is None:
                current_record['start'] = instr.address
                
            # Check if adding this would exceed max length
            current_length = sum(len(code) for code in current_record['codes'])
            new_length = current_length + len(instr.object_code)
            
            if new_length > MAX_LENGTH:
                # Flush current record and start new one
                text_records.append(self._format_text_record(current_record))
                current_record = {
                    'start': instr.address,
                    'codes': [instr.object_code]
                }
            else:
                current_record['codes'].append(instr.object_code)
                
        # Flush remaining record
        if current_record['codes']:
            text_records.append(self._format_text_record(current_record))
            
        return text_records
        
    def _format_text_record(self, record):
        """Format a text record"""
        codes = ''.join(record['codes'])
        length = len(codes) // 2  # Length in bytes
        return f"T^{record['start']:06X}^{length:02X}^{codes}"
        
    def _generate_modification_records(self, pass2_obj):
        """Generate Modification records: M^address^length"""
        mod_records = []
        
        if hasattr(pass2_obj, 'modification_records'):
            for mod in pass2_obj.modification_records:
                addr = mod['address']
                length = mod['length']
                mod_records.append(f"M^{addr:06X}^{length:02X}")
                
        return mod_records
        
    def _generate_end_record(self, instructions):
        """Generate End record: E^first_exec_address"""
        first_exec = 0
        
        # Find END directive and get its operand
        for instr in instructions:
            if instr.mnemonic == 'END':
                if instr.operand:
                    # Look up the address of the operand
                    for i in instructions:
                        if i.label == instr.operand:
                            first_exec = i.address
                            break
                break
                
        return f"E^{first_exec:06X}"
        
    def generate_listing_file(self, filename, instructions):
        """Generate listing file with addresses and object code"""
        try:
            with open(filename, 'w') as f:
                f.write("LINE  LOC    OBJECT CODE   SOURCE STATEMENT\n")
                f.write("====  ====   ===========   ================\n")
                
                for instr in instructions:
                    line_num = f"{instr.line_num:4d}"
                    
                    if instr.is_comment:
                        f.write(f"{line_num}                       {instr.original_line}\n")
                    else:
                        loc = f"{instr.address:04X}" if instr.address else "    "
                        obj_code = f"{instr.object_code:12s}" if instr.object_code else "            "
                        
                        source = f"{instr.label:8s} {instr.mnemonic:8s} {instr.operand}"
                        
                        f.write(f"{line_num}  {loc}   {obj_code}   {source}\n")
                        
            return True
            
        except Exception as e:
            print(f"Error writing listing file: {e}")
            return False


def test_output_generator():
    """Test function for OutputGenerator"""
    print("Testing OutputGenerator...")
    
    from data_structures import Instruction
    
    # Create test instructions with object code
    instructions = [
        Instruction(1, "COPY    START   1000"),
        Instruction(2, "FIRST   LDA     ALPHA"),
        Instruction(3, "        STA     BETA"),
        Instruction(4, "ALPHA   WORD    5"),
        Instruction(5, "BETA    RESW    1"),
        Instruction(6, "        END     FIRST"),
    ]
    
    # Set up data
    instructions[0].mnemonic = 'START'
    instructions[0].label = 'COPY'
    instructions[0].operand = '1000'
    instructions[0].address = 0x1000
    
    instructions[1].label = 'FIRST'
    instructions[1].mnemonic = 'LDA'
    instructions[1].operand = 'ALPHA'
    instructions[1].address = 0x1000
    instructions[1].object_code = '032026'
    
    instructions[2].mnemonic = 'STA'
    instructions[2].operand = 'BETA'
    instructions[2].address = 0x1003
    instructions[2].object_code = '0F2029'
    
    instructions[3].label = 'ALPHA'
    instructions[3].mnemonic = 'WORD'
    instructions[3].operand = '5'
    instructions[3].address = 0x1006
    instructions[3].object_code = '000005'
    instructions[3].is_directive = True
    
    instructions[4].label = 'BETA'
    instructions[4].mnemonic = 'RESW'
    instructions[4].operand = '1'
    instructions[4].address = 0x1009
    instructions[4].is_directive = True
    
    instructions[5].mnemonic = 'END'
    instructions[5].operand = 'FIRST'
    
    # Generate output
    generator = OutputGenerator()
    
    # Create mock pass2 object with modification records
    class MockPass2:
        modification_records = []
        
    success = generator.write_object_file(
        'test_output.obj',
        instructions,
        None,
        MockPass2()
    )
    
    if success:
        print("\n✓ Object file generated: test_output.obj")
        print("\nContents:")
        with open('test_output.obj', 'r') as f:
            print(f.read())
            
        import os
        os.remove('test_output.obj')
        print("✓ OutputGenerator test passed")
    else:
        print("✗ Test failed")


if __name__ == '__main__':
    test_output_generator()