"""
TODO:
    -ignore comments
    -extract definations
    -extract labels
    -decode and replace defined variables
    -update and replace labels
    -replace opcodes with hexcode
"""

INS_SET = \
    {
    'mov' : '00000','mvi' : '00001','lxi' : '00010','ldr' : '00011','str' : '00100',
    'add' : '00101','adc' : '00110','adi' : '00111','aci' : '01000','sub' : '01001',
    'sbb' : '01010','sui' : '01011','sbi' : '01100','inc' : '01101','dcr' : '01110',
    'cmp' : '01111','not' : '10000','and' : '10001','or'  : '10010','push': '10100',
    'pop' : '10101','call': '10110','ret' : '10111','jc'  : '11000','jz'  : '11001',
    'jn'  : '11010','inb' : '11011','out' : '11100','MBS' : '11101','SST' : '11110',
    'jmp' : '10011'
}

def ReadFile(filename):
    DATA = []
    DEF = []
    labels = []
    index = 0
    with open(filename,'r') as file:
        for line in file:
            tmp = []
            keywords = []
            leave = False
            for l in line:
                if l == '/':
                    break
                if line.index(l) == line.index('\n'):
                    if len(tmp) != 0:
                        keywords.append(''.join(tmp))
                if l == ' ':
                    if len(tmp) != 0:
                        keywords.append(''.join(tmp))
                        tmp = []
                    continue
                if l == ':':
                    labels.append((''.join(tmp),index))
                    tmp = []
                    continue
                tmp.append(l)
            if "@define" in keywords:
                value = keywords[2]
                if value[0] == '-':
                    value = value[1:]
                    value = int(value,16) if '0x' in value else int(value,2) if '0b' in value else int(value)
                    value = 2**8-value
                    if value < 0:   raise Exception("Invalid negative value defined")
                elif value[0] == "'" and value[len(value)-1]=="'":
                    value = value[1:-1]
                    value = ord(value)
                elif value[0] == '+':
                    value = value[1:]
                    value = int(value, 16) if '0x' in value else int(value, 2) if '0b' in value else int(value)

                DEF.append((keywords[1],str(value)))
                continue
            for key in keywords:
                for dat in DEF:
                    if key == dat[0]:
                        keywords[keywords.index(key)] = dat[1]
            if len(keywords)!=0:
                DATA.append(keywords)
                index+=1

    return DATA,labels

def OP_decode(code_set):
    # inb otb MBS ret decoded individually
    arg_r = ['0xd','0xe','0x10','0x14','0x15'] #5
    arg_r_r = ['0x0','0x5','0x6','0x9','0xa','0xf','0x11','0x12']#8
    arg_r_im8 = ['0x1','0x7','0x8','0xb','0xc']#5
    arg_r_im16 = ['0x2','0x3','0x4']#3
    arg_im16 = ['0x13','0x16','0x18','0x19','0x1a','0x1e']#6

    reg = [('a','100'),('m','000'),('b','101'),('c','001'),('d','110'),('e','010'),('h','111'),('l','011'),('bc','001'),('de','010'),('hl','011')]

    for code in code_set:
        code[0] = INS_SET[code[0]]

        if hex(int(code[0], 2)) in arg_r:
            flag = False
            for r in reg:
                if code[1] == r[0]:
                    code[0] = code[0]+r[1]
                    code[0] = hex(int(code[0],2))[2:]
                    code.pop(1)
                    flag = True
                    break
            if not flag:    raise Exception("Error : Invalid register Selected")

        elif hex(int(code[0], 2)) in arg_r_r:
            a1 = ''
            a2 = ''
            for r in reg:
                if code[2] == r[0]:
                    a2 = r[1]
                if code[1] == r[0]:
                    a1 = r[1]
                if a1!='' and a2!='':
                    break
            if a1=='' or a2=='':    raise Exception(f"Error : Invalid register Selected {code[0]} {code[1]} {code[2]}")
            code[2] = '00000'+a2
            code[2] = '0'+hex(int(code[2],2))[2:]
            code[0] = code[0]+a1
            code[0] = hex(int(code[0], 2))[2:]
            code[0] = code[0] if len(code[0]) == 2 else '0' + code[0]
            code.pop(1)

        elif hex(int(code[0], 2)) in arg_r_im8:
            if code[2][0] == '"' or code[2][0] == "'":
                val = ord(code[2][1])
                val = hex(val)
            else:
                val = hex(int(code[2],16)) if '0x' in code[2] else hex(int(code[2],2)) if '0b' in code[2] else hex(int(code[2]))
            val = val[2:]
            if len(val)>2:  raise Exception(f"\nError : parameter exceeded the max value\n line :  {code[0]} {code[1]} {code[2]}")
            val = '0'+val if len(val)==1 else val
            flag = False
            for r in reg:
                if code[1] == r[0]:
                    code[0] = code[0]+r[1]
                    code[0] = hex(int(code[0], 2))[2:]
                    code[0] = '0'+code[0] if len(code[0])==1 else code[0]
                    code[2] = val
                    code.pop(1)
                    flag = True
                    break
            if not flag:    raise Exception(f"Error : Invalid register Selected\n\tline : {code[0]} {code[1]} {code[2]}")

        elif hex(int(code[0], 2)) in arg_r_im16:
            flag = False
            for r in reg:
                if code[1] == r[0]:
                    code[0] = code[0]+r[1]
                    code[0] = hex(int(code[0], 2))[2:]
                    code[0] = code[0] if len(code[0]) == 2 else '0' + code[0]
                    code[1] = code[2]
                    flag = True
                    break
            if not flag:    raise Exception(f"Error : Invalid register Selected\n\tline : {code[0]} {code[1]} {code[2]}")

        elif hex(int(code[0], 2)) in arg_im16:
            code[0] = code[0]+'000'
            code[0] = hex(int(code[0], 2))[2:]
            code.append("h")

        elif hex(int(code[0], 2)) == '0x1b':  # inb %r [PORT]
            flag = False
            for r in reg:
                if code[1] == r[0]:
                    code[0] = code[0]+r[1]
                    code[0] = hex(int(code[0], 2))[2:]
                    code[0] = code[0] if len(code[0]) == 2 else '0' + code[0]
                    code[2] = hex(int(code[2]+'0000',2))[2:]
                    code.pop(1)
                    flag = True
                    break
            if not flag:    raise Exception(f"Error : Invalid register Selected\n\tline : {code[0]} {code[1]} {code[2]}")

        elif hex(int(code[0], 2)) == '0x1c': # otb [PORT] %r
            flag = False
            for r in reg:
                if code[2] == r[0]:
                    code[0] = code[0] + '000'
                    code[0] = hex(int(code[0], 2))[2:]
                    code[0] = code[0] if len(code[0]) == 2 else '0' + code[0]
                    code[1] = code[1]+'0'+r[1]
                    code[1] = hex(int(code[1],2))[2:]
                    code.pop(2)
                    flag = True
                    break
            if not flag:    raise Exception(f"Error : Invalid register Selected\n\tline : {code[0]} {code[1]} {code[2]}")

        elif hex(int(code[0], 2)) == '0x1d':    #MBS imm8
            code[0] = code[0]+'000'
            code[0] = hex(int(code[0], 2))[2:]
            code[1] = hex(int(code[1],16))[2:] if '0x' in code[1] else hex(int(code[1],2))[2:] if '0b' in code[1] else hex(int(code[1]))[2:]
            code[1] = '0'+code[1] if len(code[1])==1 else code[1]

        elif hex(int(code[0],2)) == '0x17': #ret
            code[0] = code[0]+'000'
            code[0] = hex(int(code[0], 2))[2:]
            code[0] = code[0] if len(code[0]) == 2 else '0' + code[0]

        else:
            raise Exception("Invalid Opcode")

def label_parser(data,labels):
    nlabels = []
    current_addr = 0
    extra_byte = 0
    for i,code in enumerate(data):
        for label in labels:
            if label[1] == i:
                nlabels.append((label[0],label[1]+extra_byte))
                break
        for j,ins in enumerate(code):
            if '$' in ins:
                if '+' in ins:
                    x = ins[ins.index('+')+1:]
                    x = int(x[2:],16) if x[:2]=='0x' else int(x[2:],2) if x[:2]=='0b' else int(x)
                    y = 0
                    for k in range(x):
                        y += len(data[i + k])
                    code[j] = hex(current_addr + y)
                elif '-' in ins:
                    x = ins[ins.index('-') + 1:]
                    x = int(x[2:], 16) if x[:2] == '0x' else int(x[2:], 2) if x[:2] == '0b' else int(x)
                    y = 0
                    for k in range(x):
                        y+=len(data[i-k-1])
                    code[j] = hex(current_addr-y)
                else:
                    code[j] = hex(current_addr)

        current_addr += len(code)
        extra_byte+=len(code)-1
    labels = nlabels
    for code in data:

        for label in labels:
            if label[0] in code:
                addr = hex(label[1])
                code[1] = addr
                break

        if len(code)==3:
            code[1] = code[1] if '0x' in code[1] else hex(int(code[1],2)) if '0b' in code[1] else hex(int(code[1]))
            code[1] = code[1][2:]
            code[1] = '0'*(4-len(code[1]))+code[1]
            code[2] = code[1][2:]
            code[1] = code[1][:2]
    return labels

def create_ins_array(data):
    new_data = []
    for block in data:
        for code in block:
            new_data.append(code)
    return new_data

def generate_writable_data(data):
    new_data = []
    tmp = []
    size = (int(len(data)/16)+1)*16
    for i in range(size+1):
        if i%16 == 0 and i>0:
            val = '\n'+'0'*(i<32)+hex(i-16)[2:]+' : '+' '.join(tmp)
            new_data.append(val)
            tmp = []
        dat = '00' if i>=len(data) else data[i]
        tmp.append(dat)
    return new_data


def main():
    cleaned_data,labels = ReadFile("temp.txt") #defined values are replaced
    #print(cleaned_data)
    OP_decode(cleaned_data)                         #opcodes are decoded
    #print(cleaned_data)
    labels = label_parser(cleaned_data,labels)      #labels are updated and parsed with new addresses
    #print(cleaned_data)
    code_array = create_ins_array(cleaned_data)
    print(code_array, '\n\n', labels, '\n')
    writable_file = generate_writable_data(code_array)
    writable_file = ["v3.0 hex words addressed"]+writable_file
    with open("machinecode.ss",'w') as file:
        file.writelines(writable_file)

if __name__ == "__main__":
    main()

