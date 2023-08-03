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

def GetData():
    DATA = []
    with open("../OverView.txt") as file:
        collect = False
        for line in file:
            line = line.rstrip()

            if line == "========Instructions========":
                collect = True
                continue
            if not collect:
                continue
            if line[0] == "#":
                continue
            word = line[:11]
            while word[len(word)-1]==" ":
                word = word[:-1]
            opcode = word[word.index(":")+2:]
            hexcode = word[:word.index(":")-1]
            DATA.append((opcode,hexcode))
    to_bin = lambda x:"0"*(5-len(x))+x
    dictionary = {data[0] : to_bin(bin(int(data[1],16))[2:]) for data in DATA}
    return dictionary

def Convert_to_bin(code):
    ALU = ["nx","zy","ny","f","no","ce"]
    _OC = ["~mo","alo","rd","%ro"]
    _IC = ["xx","wz","%ri","ii"]
    _PTRC = ["*hl","*pc","*sp","*wz"]
    EXTRA = ["wr","^h","pc->r","we","mbi","rbi","p/s","i/d","~wz","ovr"]
    alu = ['0' for i in range(6)]
    _oc = '00'
    _ic = '00'
    _ptrc = '00'
    extra = ['0' for i in range(10)]
    for ins in code:
        if ins in ALU:
            alu[ALU.index(ins)] = '1'
        elif ins in _OC:
            t = bin(_OC.index(ins))[2:]
            _oc = '0'+t if len(t)==1 else t
        elif ins in _IC:
            t = bin(_IC.index(ins))[2:]
            _ic = '0'+t if len(t)==1 else t
        elif ins in _PTRC:
            t = bin(_PTRC.index(ins))[2:]
            _ptrc = '0'+t if len(t)==1 else t
        elif ins in EXTRA:
            extra[EXTRA.index(ins)] = '1'
        else:
            print("Invalid Instruction")

    return ''.join(alu)+_oc+_ic+_ptrc+''.join(extra)

def fetch():
    codeblock = [["*pc","~mo"],["~mo","ii","rbi","ovr"]]
    data = []
    for i in range(31):
        for c in range(2):
            clk = "00"+bin(c)[2:]
            opcode = bin(i)[2:]
            opcode = "0"*(5-len(opcode))+opcode
            bin_data = Convert_to_bin(codeblock[c])
            inp = clk+opcode
            data.append((inp,bin_data))
    return data

def Generate():
    data = []
    with open("../microcode.txt") as file:
        opcode = ''
        collect = False
        for line in file:
            line = line.rstrip()

            if line[0] == '@':
                opcode = line[1:line.index(' ')] if ' ' in line else line[1:]

                clk = 2
                continue
            if opcode == "fetch":    continue

            while line[0] == " ":
                line = line[1:]
            while line[len(line)-1] == " ":
                line = line[:-1]
            code = line.split(' ')
            c = bin(clk)[2:]
            c = (3-len(c))*"0"+c
            clk += 1
            inp = c+INS_SET[opcode]
            bin_data = Convert_to_bin(code)
            data.append((inp,bin_data))
    return data

def Getkey(val,sets):
    for key,value in sets.items():
        if val == value:
            return key
    return "error"


def decode(LST,string):
    data = []
    for i,l in enumerate(string):
        if l == '1':
            data.append(LST[i])
    return ' '.join(data)

def Debug(data):
    ALU = ["nx", "zy", "ny", "f", "no", "ce"]
    _OC = ["~mo", "alo", "rd", "%ro"]
    _IC = ["xx", "wz", "%ri", "ii"]
    _PTRC = ["*hl", "*pc", "*sp", "*wz"]
    EXTRA = ["wr", "^h", "pc->r", "we", "mbi", "rbi", "p/s", "i/d", "~wz", "ovr"]
    prev = ''
    for code in data:
        inp = code[0]
        out = code[1]
        alu = out[:6]
        _oc = out[6:8]
        _ic = out[8:10]
        _ptrc = out[10:12]
        extra = out[12:]
        clk = inp[:3]
        opcode = inp[3:]
        if opcode != prev:
            print(f"@{Getkey(opcode,INS_SET)}:")
            prev = opcode
        print("\t",decode(ALU,alu),end=' ')

        print(_OC[int(_oc,2)],end=' ')
        if _ic != "00":
            print(_IC[int(_ic,2)],end=' ')

        print(_PTRC[int(_ptrc,2)],end=' ')
        print(decode(EXTRA,extra),end=' \n')

def to_hex(microcode):
    for i in range(256):
        if i % 8 == 0:
            print(f"\n{hex(i)[2:]} : ",end='')
        s = "000000"
        for data in microcode:
            address = int(data[0],2)
            code = hex(int(data[1],2))[2:]
            code = "0"*(6-len(code))+code
            if i == address:
                s = code
                break
        print(s,end=' ')


def main():
    FETCH_DATA = fetch()
    MICROCODE = Generate()
    code = FETCH_DATA+MICROCODE
    #Debug(MICROCODE)
    to_hex(code)


if __name__ == "__main__":
    main()
