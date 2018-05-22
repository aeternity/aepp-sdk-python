
# AEVM opcodes
#
# as defined in /epoch/apps/aebytecode/include/aeb_opcodes.hrl
#
import binascii

# based on https://github.com/holiman/evmlab/blob/master/evmlab/opcodes.py
#
# gas prices might differ for AE

# schema: [opcode, ins, outs, gas, arguments]
OPCODES = {
    0x00: ('STOP', 0, 0, 0, 0),
    0x01: ('ADD', 2, 1, 3, 0),
    0x02: ('MUL', 2, 1, 5, 0),
    0x03: ('SUB', 2, 1, 3, 0),
    0x04: ('DIV', 2, 1, 5, 0),
    0x05: ('SDIV', 2, 1, 5, 0),
    0x06: ('MOD', 2, 1, 5, 0),
    0x07: ('SMOD', 2, 1, 5, 0),
    0x08: ('ADDMOD', 3, 1, 8, 0),
    0x09: ('MULMOD', 3, 1, 8, 0),
    0x0a: ('EXP', 2, 1, 10, 0),
    0x0b: ('SIGNEXTEND', 2, 1, 5, 0),
    0x10: ('LT', 2, 1, 3, 0),
    0x11: ('GT', 2, 1, 3, 0),
    0x12: ('SLT', 2, 1, 3, 0),
    0x13: ('SGT', 2, 1, 3, 0),
    0x14: ('EQ', 2, 1, 3, 0),
    0x15: ('ISZERO', 1, 1, 3, 0),
    0x16: ('AND', 2, 1, 3, 0),
    0x17: ('OR', 2, 1, 3, 0),
    0x18: ('XOR', 2, 1, 3, 0),
    0x19: ('NOT', 1, 1, 3, 0),
    0x1a: ('BYTE', 2, 1, 3, 0),
    0x20: ('SHA3', 2, 1, 30, 0),
    0x30: ('ADDRESS', 0, 1, 2, 0),
    0x31: ('BALANCE', 1, 1, 20, 0),
    0x32: ('ORIGIN', 0, 1, 2, 0),
    0x33: ('CALLER', 0, 1, 2, 0),
    0x34: ('CALLVALUE', 0, 1, 2, 0),
    0x35: ('CALLDATALOAD', 1, 1, 3, 0),
    0x36: ('CALLDATASIZE', 0, 1, 2, 0),
    0x37: ('CALLDATACOPY', 3, 0, 3, 0),
    0x38: ('CODESIZE', 0, 1, 2, 0),
    0x39: ('CODECOPY', 3, 0, 3, 0),
    0x3a: ('GASPRICE', 0, 1, 2, 0),
    0x3b: ('EXTCODESIZE', 1, 1, 20, 0),
    0x3c: ('EXTCODECOPY', 4, 0, 20, 0),
    0x3d: ('RETURNDATASIZE', 0, 1, 2, 0),
    0x3e: ('RETURNDATACOPY', 3, 0, 3, 0),
    0x40: ('BLOCKHASH', 1, 1, 20, 0),
    0x41: ('COINBASE', 0, 1, 2, 0),
    0x42: ('TIMESTAMP', 0, 1, 2, 0),
    0x43: ('NUMBER', 0, 1, 2, 0),
    0x44: ('DIFFICULTY', 0, 1, 2, 0),
    0x45: ('GASLIMIT', 0, 1, 2, 0),
    0x50: ('POP', 1, 0, 2, 0),
    0x51: ('MLOAD', 1, 1, 3, 0),
    0x52: ('MSTORE', 2, 0, 3, 0),
    0x53: ('MSTORE8', 2, 0, 3, 0),
    0x54: ('SLOAD', 1, 1, 50, 0),
    0x55: ('SSTORE', 2, 0, 0, 0),
    0x56: ('JUMP', 1, 0, 8, 0),
    0x57: ('JUMPI', 2, 0, 10, 0),
    0x58: ('PC', 0, 1, 2, 0),
    0x59: ('MSIZE', 0, 1, 2, 0),
    0x5a: ('GAS', 0, 1, 2, 0),
    0x5b: ('JUMPDEST', 0, 0, 1, 0),

    0x60: ('PUSH1', 0, 0, 0, 1),
    0x61: ('PUSH2', 0, 0, 0, 2),
    0x62: ('PUSH3', 0, 0, 0, 3),
    0x63: ('PUSH4', 0, 0, 0, 4),
    0x64: ('PUSH5', 0, 0, 0, 5),
    0x65: ('PUSH6', 0, 0, 0, 6),
    0x66: ('PUSH7', 0, 0, 0, 7),
    0x67: ('PUSH8', 0, 0, 0, 8),
    0x68: ('PUSH9', 0, 0, 0, 9),
    0x69: ('PUSH10', 0, 0, 0, 10),
    0x6a: ('PUSH11', 0, 0, 0, 11),
    0x6b: ('PUSH12', 0, 0, 0, 12),
    0x6c: ('PUSH13', 0, 0, 0, 13),
    0x6d: ('PUSH14', 0, 0, 0, 14),
    0x6e: ('PUSH15', 0, 0, 0, 15),
    0x6f: ('PUSH16', 0, 0, 0, 16),
    0x70: ('PUSH17', 0, 0, 0, 17),
    0x71: ('PUSH18', 0, 0, 0, 18),
    0x72: ('PUSH19', 0, 0, 0, 19),
    0x73: ('PUSH20', 0, 0, 0, 20),
    0x74: ('PUSH21', 0, 0, 0, 21),
    0x75: ('PUSH22', 0, 0, 0, 22),
    0x76: ('PUSH23', 0, 0, 0, 23),
    0x77: ('PUSH24', 0, 0, 0, 24),
    0x78: ('PUSH25', 0, 0, 0, 25),
    0x79: ('PUSH26', 0, 0, 0, 26),
    0x7a: ('PUSH27', 0, 0, 0, 27),
    0x7b: ('PUSH28', 0, 0, 0, 28),
    0x7c: ('PUSH29', 0, 0, 0, 29),
    0x7d: ('PUSH30', 0, 0, 0, 30),
    0x7e: ('PUSH31', 0, 0, 0, 31),
    0x7f: ('PUSH32', 0, 0, 0, 32),
    0x80: ('DUP1', 0, 0, 0, 0),
    0x81: ('DUP2', 0, 0, 0, 0),
    0x82: ('DUP3', 0, 0, 0, 0),
    0x83: ('DUP4', 0, 0, 0, 0),
    0x84: ('DUP5', 0, 0, 0, 0),
    0x85: ('DUP6', 0, 0, 0, 0),
    0x86: ('DUP7', 0, 0, 0, 0),
    0x87: ('DUP8', 0, 0, 0, 0),
    0x88: ('DUP9', 0, 0, 0, 0),
    0x89: ('DUP10', 0, 0, 0, 0),
    0x8a: ('DUP11', 0, 0, 0, 0),
    0x8b: ('DUP12', 0, 0, 0, 0),
    0x8c: ('DUP13', 0, 0, 0, 0),
    0x8d: ('DUP14', 0, 0, 0, 0),
    0x8e: ('DUP15', 0, 0, 0, 0),
    0x8f: ('DUP16', 0, 0, 0, 0),
    0x90: ('SWAP1', 0, 0, 0, 0),
    0x91: ('SWAP2', 0, 0, 0, 0),
    0x92: ('SWAP3', 0, 0, 0, 0),
    0x93: ('SWAP4', 0, 0, 0, 0),
    0x94: ('SWAP5', 0, 0, 0, 0),
    0x95: ('SWAP6', 0, 0, 0, 0),
    0x96: ('SWAP7', 0, 0, 0, 0),
    0x97: ('SWAP8', 0, 0, 0, 0),
    0x98: ('SWAP9', 0, 0, 0, 0),

    0xa0: ('LOG0', 2, 0, 375, 0),
    0xa1: ('LOG1', 3, 0, 750, 0),
    0xa2: ('LOG2', 4, 0, 1125, 0),
    0xa3: ('LOG3', 5, 0, 1500, 0),
    0xa4: ('LOG4', 6, 0, 1875, 0),
    0xf0: ('CREATE', 3, 1, 32000, 0),
    0xf1: ('CALL', 7, 1, 40, 0),
    0xf2: ('CALLCODE', 7, 1, 40, 0),
    0xf3: ('RETURN', 2, 0, 0, 0),
    0xf4: ('DELEGATECALL', 6, 0, 40, 0),
    0xfa: ('STATICCALL', 6, 1, 40, 0),
    0xfd: ('REVERT', 2, 0, 0, 0),
    0xff: ('SUICIDE', 1, 0, 0, 0),
}


def pretty_bytecode(bytecode_as_hex):
    if bytecode_as_hex.startswith('0x'):
        bytecode_as_hex = bytecode_as_hex[2:]
    bytecode_as_bytes = binascii.unhexlify(bytecode_as_hex)

    i = 0
    while i < len(bytecode_as_bytes):
        opcode = bytecode_as_bytes[i]
        name, ins, outs, gas, consumes = OPCODES.get(opcode, (f'UNKNOWN ({opcode})!', 0, 0, 0))
        arguments = bytecode_as_bytes[i + 1:i + 1 + consumes]
        arguments_ascii = arguments.decode('ascii', errors='replace')
        arguments_hex = binascii.hexlify(arguments).decode('ascii')
        pos = '0x%04x' % i
        if arguments:
            print(pos, name, arguments_hex, f'"{arguments_ascii}"')
        else:
            print(pos, name)
        i += 1 + consumes
