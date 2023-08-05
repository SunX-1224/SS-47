# ========== SS47-2 ===========

Architecture : 8 bit Von-Neumann
Addressable memory : 64KB
Total available memory : 4MB

**=======Memory Layout========**
  * 16KB ROM
  * 16KB Banked Memory
  * 30KB GP RAM
  * 2KB STACK
  * 9 General Purpose Registers (3 pairable and Accumulator)
  * Program Counter 16b
  * Stack Pointer 16b
  * Memory Bank Register(3-255)
  * 4MB total available memory with 64KB addressable and remaining banked memory *

**========Instructions========**
    0x00 : mov  %r1 %r2         : %r1 = %r2
    0x01 : mvi  %r imm8         : %r = imm8
    0x02 : lxi  %rp imm16       : %rh = imm16(>8) %rl = imm16(>0)
    0x03 : ldr  %r imm16        : %r = [imm16]
    0x04 : str  %r imm16        : [imm16] = %r
    0x05 : add  %r1 %r2         : %r1 = %r1 + %r2
    0x06 : adc  %r1 %r2         : %r1 = %r1 + %r2 + c
    0x07 : adi  %r imm8         : %r =%r + $imm8
    0x08 : aci  %r imm8         : %r = %r + $imm8 + c
    0x09 : sub  %r1 %r2         : %r1 = %r1 - %r2
    0x0a : sbb  %r1 %r2         : %r1 = %r1 - %r2 - b
    0x0b : sui  %r imm8         : %r = %r - $imm8
    0x0c : sbi  %r imm8         : %r = 5r - $imm8 - b
    0x0d : inc  %r              : %r++
    0x0e : dcr  %r              : %r--
    0x0f : cmp  %r1 %r2         : %r1 - %r2 -> f
    0x10 : not  %r              : %r = ! %r
    0x11 : and  %r1 %r2         : %r1 = %r1 & %r2
    0x12 : or   %r1 %r2         : %r1 = %r1 | %r2
    0x13 : jmp  imm16           : pc = imm16
    0x14 : push %r              : [--SP] = %r
    0x15 : pop  %r              : %r = [SP++]
    0x16 : call imm16           : wz = imm16 => [--SP] = pcl => [--SP] = pch => pc = wz
    0x17 : ret                  : w = [SP++] => z = [SP++] => PCe ovr
    0x18 : jc   imm16           : if c == 1? PC = imm16 : NOP
    0x19 : jz   imm16           : if z == 1? PC = imm16 : NOP
    0x1a : jn   imm16           : if n == 1? PC = imm16 : NOP
    0x1b : inb  %r [PORT]       : %r = [PORT]
    0x1c : out  [PORT] %r       : [PORT] = %r
    0x1d : MBS  imm8            : mbr = $imm8
    0x1e : SST  imm16           : sp = $imm16
    #0x1f : ji  imm16           : if i == 1? PC = imm16 : NOP   //not implemented (reserved for interrupts)

  ***Note : the syntax is case dependent***

**========== Registers ===========**
Pairs code :^h|^l  001
             A|M : 00   :: A:100  M:000
             B|C : 01   :: B:101  C:001
             D|E : 10   :: D:110  E:010
             H|L : 11   :: H:111  L:011
  
Register Pair should be indicated by the low-byte storing register in the pair. if specific register is to be accessed the 2lsb should indicate pair and 1msb should indicate if the register stores high byte or low byte in the pair. M indicates the memory location in RAM indicated by hl pair or immediate 16bits.

  ***Note : Pairs code is provided just in case the user wants to translate the op-code to machine code by hand.***

**========== Input/Output ==========**
Four specific ports are available for input and output purpose. Otherwise any number of ports can be used in certain memory address block by using interfacing chip (for this method instead of inb/out instruction, memory instructions ldr/str has to be used). These four pairs are indicated by 4msb in the location buffer. Output can be supplied through multiple ports but input is available through one port at a time whose priority is decoded inside the cpu, so it is recommended to select one port at a time for input and output purpose.
  
**========== Memory banking ==========**
Memory banking is available for 16KB memory of the RAM. Total 253 memories can be banked which makes the total available banked memory of 253*16KB of banked memory and and 48 KB reserved memory that makes total of 4MB of memory that can be used with microprocessor. 
