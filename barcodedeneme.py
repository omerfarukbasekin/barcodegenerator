# Set FCC constants
FCC_37_CUST = "11"
FCC_37_ROUT = "87"
FCC_37_REPL = "45"
FCC_37_REDI = "92"
FCC_52_FF_MET = "59"
FCC_67_FF_MET = "62"
FCC_67_FF_MAN = "44"

# Barcode stop and start symbols
BC_START_SYM = "13"
BC_STOP_SYM = "13"

# Return status codes and corresponding messages
BC_OK = 0
BC_INV_FCC = 1
BC_INV_SORT_CODE = 2
BC_INV_CUST_INFO = 3
BC_INV_ENCODE_STR = 4
BC_INV_RANGE = 5

bcmsg = [
    "Barcode successfully encoded",
    "Invalid Format Control field",
    "Invalid Sorting Code field",
    "Invalid customer information field",
    "Unable to encode data",
    "Invalid barcode range"
]

# Structure for the 4 parity symbols of the Reed-Solomon error correction block
class ParityString:
    def __init__(self):
        self.in_ = [0, 0, 0, 0]

# Global variables
mult = [[0] * 64 for _ in range(64)]
gen = [0, 0, 0, 0, 0]

NSET = "01234567890"
NTable = ["00", "01", "02", "10", "11", "12", "20", "21", "22", "30"]

CNTable = ["222", "300", "301", "302", "310", "311", "312", "320", "321", "322"]

ZSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ZTable = [
    "000", "001", "002", "010", "011", "012", "020", "021", "022", "100",
    "101", "102", "110", "111", "112", "120", "121", "122", "200", "201",
    "202", "210", "211", "212", "220", "221"
]

CSET = "abcdefghijklmnopqrstuvwxyz #"
CTable = [
    "023", "030", "031", "032", "033", "103", "113", "123", "130", "131",
    "132", "133", "203", "213", "223", "230", "231", "232", "233", "303",
    "313", "323", "330", "331", "332", "333", "003", "013"
]

BarTable = [
    "000", "001", "002", "003", "010", "011", "012", "013", "020", "021",
    "022", "023", "030", "031", "032", "033", "100", "101", "102", "103",
    "110", "111", "112", "113", "120", "121", "122", "123", "130", "131",
    "132", "133", "200", "201", "202", "203", "210", "211", "212", "213",
    "220", "221", "222", "223", "230", "231", "232", "233", "300", "301",
    "302", "303", "310", "311", "312", "313", "320", "321", "322", "323",
    "330", "331", "332", "333"
]

def GetBCSymbol(c):
    if c.isdigit():
        return NTable[int(c)]
    elif c.isupper():
        return ZTable[ZSET.index(c)]
    elif c.islower() or c == '#' or c == ' ':
        return CTable[CSET.index(c)]
    else:
        return "023"

def MultiplyTable():
    global mult
    for i in range(64):
        for j in range(64):
            mult[i][j] = (i * j) % 64

def GenPoly():
    global gen
    gen[0] = 4
    gen[1] = 31
    gen[2] = 14
    gen[3] = 0
    gen[4] = 9

def Multiply(p, q):
    result = 0
    if p != 0 and q != 0:
        result = mult[p][q]
    return result

def InitBarCode():
    MultiplyTable()
    GenPoly()

def CharEncode(ch, odd, even):
    odd.append(int(ch[0]))
    even.append(int(ch[1]))

def CharDecode(odd, even):
    ch = ""
    ch += str(odd)
    ch += str(even)
    return ch

def GenPString(cs, ps):
    ps.in_[0] = Multiply(cs[0], gen[0]) ^ Multiply(cs[1], gen[1]) ^ Multiply(cs[2], gen[2]) ^ Multiply(cs[3], gen[3]) ^ Multiply(cs[4], gen[4])
    ps.in_[1] = Multiply(cs[0], gen[1]) ^ Multiply(cs[1], gen[2]) ^ Multiply(cs[2], gen[3]) ^ Multiply(cs[3], gen[4]) ^ Multiply(cs[4], gen[0])
    ps.in_[2] = Multiply(cs[0], gen[2]) ^ Multiply(cs[1], gen[3]) ^ Multiply(cs[2], gen[4]) ^ Multiply(cs[3], gen[0]) ^ Multiply(cs[4], gen[1])
    ps.in_[3] = Multiply(cs[0], gen[3]) ^ Multiply(cs[1], gen[4]) ^ Multiply(cs[2], gen[0]) ^ Multiply(cs[3], gen[1]) ^ Multiply(cs[4], gen[2])

def BuildBarcode(fcc, sortcode, custinfo):
    if len(fcc) != 2:
        return BC_INV_FCC
    if len(sortcode) != 4:
        return BC_INV_SORT_CODE
    if len(custinfo) > 8:
        return BC_INV_CUST_INFO

    barcode = BC_START_SYM
    barcode += GetBCSymbol(fcc[0])
    barcode += GetBCSymbol(fcc[1])
    barcode += GetBCSymbol(sortcode[0])
    barcode += GetBCSymbol(sortcode[1])
    barcode += GetBCSymbol(sortcode[2])
    barcode += GetBCSymbol(sortcode[3])
    barcode += GetBCSymbol(custinfo[0])
    barcode += GetBCSymbol(custinfo[1])
    barcode += GetBCSymbol(custinfo[2])
    barcode += GetBCSymbol(custinfo[3])
    barcode += GetBCSymbol(custinfo[4])
    barcode += GetBCSymbol(custinfo[5])
    barcode += GetBCSymbol(custinfo[6])
    barcode += GetBCSymbol(custinfo[7])

    barcode += BC_STOP_SYM

    length = len(barcode)
    k = 0
    pstr = ParityString()

    for i in range(length):
        ch = barcode[i]
        odd = []
        even = []

        CharEncode(ch, odd, even)
        GenPString(odd, pstr)
        barcode = barcode[:i + k] + CharDecode(odd, even) + barcode[i + k + 1:]
        k += 2

    barcode = barcode[:length + k]
    barcode += CharDecode(pstr.in_, [])

    return BC_OK, barcode

# Example usage
fcc = "37"
sortcode = "1234"
custinfo = "ABCD1234"

InitBarCode()
status, barcode = BuildBarcode(fcc, sortcode, custinfo)

if status == BC_OK:
    print(bcmsg[status])
    print("Barcode:", barcode)
else:
    print(bcmsg[status])
