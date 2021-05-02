"""
Author :  D Hakesh CS19B017

Assignment 8 : Pipe Line Design Using Python

Note : Require Python 2.7 or more version to run.

Input files paths assumed in programm: (line numbers 36, 44, 52)
'sample_tc/input/ICache.txt'
'sample_tc/input/DCache.txt'
'sample_tc/input/RF.txt'

"""


import math

############# Metric - variables and global variables ###########################################################

instructions = arthmetic_instructions = logical_instructions = data_instructions = control_instructions = halt_instructions = cpi = stalls = data_stalls = control_stalls = 0


#store 8 bit information as strings
lcache = dcache = RF = []

PC = 0
IR = ""
record = []

####################################  Reading from files ####################################################

#Read from lcache.txt to lcache[]
f = open( 'sample_tc/input/ICache.txt')
temp_l = f.readlines()
lcache = [ bin(int(i[0], base = 16))[2:].zfill(4) + bin(int(i[1], base = 16))[2:].zfill(4)  for i in temp_l]
f.close()



#Read from dcache.txt to dcache[]
f = open( 'sample_tc/input/DCache.txt')
temp_d = f.readlines()
dcache = [ bin(int(i[0], base = 16))[2:].zfill(4) + bin(int(i[1], base = 16))[2:].zfill(4)  for i in temp_d]
f.close()



#Read from RF.txt to RF[]
f = open( 'sample_tc/input/RF.txt')
temp_rf = f.readlines()
RF = [ bin(int(i[0], base = 16))[2:].zfill(4) + bin(int(i[1], base = 16))[2:].zfill(4)  for i in temp_rf]
f.close()


################### SOME USEFUL FUNCTIONS #####################################################
#convert given into integer into signed binary string(8 bit).
def tobin(x):
    if( x >= 0):
        return bin(x)[2:].zfill(8)
    else :
        return bin(x & 0xff)[2:]

#convert given given "signed" binary string into integer number.
def comp2(binary, bits = 8):
    val = int( binary , 2)
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

#update metrics according to given opcode
def metric_typeInstruction(opcode):
    global arthmetic_instructions, logical_instructions, data_instructions, control_instructions,halt_instructions
    oper = int(opcode,2)
    if(oper < 4):arthmetic_instructions += 1
    if(oper > 3 and oper < 8):logical_instructions += 1
    if(oper == 8 or oper == 9):data_instructions += 1
    if(oper == 10 or oper == 11):control_instructions += 1
    if(oper == 15):halt_instructions += 1

########################################## Data hazard Detection  ########################################################
def data_hazard():
    """
    Checks previous two instructions in record .. whether they are True dependency with current Instruction (IR).
    We use boolean array "wait[r1]" indicates availability of true data.
    we refine reg - r2 and r3 according to opcode to identify correct true dependencies.

    Returns no.of stalls to happen according to record of instructions.
    """
    l = len(record)
    if(l == 0): return 0

    oper = IR[:4]

    r2 = int(IR[8:12],2)
    r3 = int(IR[12:16],2)

    if(oper == "1111" or oper == "1010"):return 0
    if(oper == "0011" or oper == "1011"):r2 = int(IR[4:8],2); r3 = 16
    if(oper == "0110"): r3 = 16
    if(oper == "1000" or oper == "1001"): r2 = int(IR[4:8],2); r3 = int(IR[8:12],2)

    for i in range(1,3):
        if(l < i):continue

        instr = record[-i]
        opera = int(instr[:4], 2)

        if(opera > 8):continue
        
        r1 = int(instr[4:8],2)
        if(wait[r1] == False): continue

        if(r1 == r2 or r1 == r3): return 3-i

    return 0

#####################################    stages Functions  ##################################################

def InstructionFetch(branch_taken, branch_target):
    # IR is a 4 char string
    # PC is a number int
    global PC, record, IR

    if(IR != ''): record.append(IR)

    if( branch_taken == 0):     # this means if branch is not taken we continue with address pointed by PC
        IR = str(lcache[PC]) + str(lcache[PC + 1])
        PC += 2
        return 
    if( branch_taken == 1):     # else go to branch target address and execute that insturction
        IR = lcache[int(branch_target,base = 2)] + lcache[int(branch_target,base = 2) + 1]
        PC = int(branch_target,base = 2) + 2
    

def InstructionDecode():
    # opcode is a string of one char ( hexa decimal )
    # A , B are ints( not 2's compleneted)
    opcode = IR[0:4]    #opcode is first(most significant) 4 bits of instruction register
    A = ""
    B = ""

    if( opcode == '1000' or opcode == '1001'):  # load or store
        A = RF[int(IR[8:12],2)]     # read content of register specified in instruction
        if( IR[12] == '0'):         # if value is non-negative then do 0 sign extension else 1
            B = '0000' + IR[12:16]  # making B as 8 bit data
        else:
            B = '1111' + IR[12:16]
        
    
    elif( opcode == '1010' ):  #jmp
        B = IR[4:12]

    elif( opcode == '1011' ): #beqz
        A = RF[int(IR[4:8],2)]
        B =  IR[8:16]

    else: #alu
        A = RF[int(IR[8:12],2)]
        B = RF[int(IR[12:16],2)]
        
        if( opcode == "0011" ):     #increment
            A = RF[int(IR[4:8],base = 2)]

    return opcode , A, B




def Execute(opcode, A, B):
    Cond = False
    AluOutput = ''

    if( opcode == '0000'): #add
        AluOutput  = tobin(comp2(A) + comp2(B))
        #print(AluOutput, comp2(A), comp2(B))
    
    if( opcode == '0001'): #sub
        AluOutput = tobin(comp2(A) - comp2(B))
        

    if( opcode == '0010'): #mul
        AluOutput = tobin( comp2(A) * comp2(B))
        #doubt : overflow

    if( opcode == '0100'): # AND
        AluOutput = tobin( comp2(A) & comp2(B))

    if( opcode == '0101'): #OR
        AluOutput = tobin( comp2(A) | comp2(B))

    if( opcode == '0110'): #NOT
        AluOutput = tobin( ~comp2(A))

    if( opcode == '0111'): #XOR
        AluOutput = tobin( comp2(A) ^ comp2(B))

    if( opcode == '1011'):  # bezq
        AluOutput = tobin(PC + comp2(B)*2)
        Cond = True if (A == '00000000') else False

    if( opcode == '1010'): #jmp
        AluOutput = tobin(PC + comp2(B)*2)
    
    if( opcode == '1000' or opcode == '1001'): # load or store
        AluOutput  = tobin(comp2(A) + comp2(B))
        
    
    if( opcode == '0011'): #inc
        AluOutput = tobin(comp2(A) + 1)

    
    return AluOutput,  Cond



def Memory(opcode, reg, eff_address):
    data = ''
    if( opcode == '1000' or opcode == '1001'):
        if( opcode == '1000'): # load
            data = dcache[int(eff_address, base = 2)]
        if( opcode == '1001'): #store
            dcache[int(eff_address, base = 2)] = RF[int(reg, base = 2)]

    return data 





def WriteBack(opcode, reg, lmd, result):
    if(int(opcode, 2) <= 8):    # writing into register specified by alu instruction
        RF[int(reg, base = 2)] = result

    if( opcode == '1000'): # load
        RF[int(reg, base = 2)] = lmd 

    

###########################################  Manager of stages  ################################################

#keep track of which stages to be executed in each cycle.
stage = [1,0,0,0,0]

#Tempory Registers used to store intermiedates.
A = B = ALUOutput = LMD = ""
cond = False

#IF [Buff1] ID [Buff2] EX [Buff3] Mem [Buff4] WB 
#Buffers between stages
buff1 = buff2 = buff3 = buff4 = ""

#indicate type of stall
raw = cont = stall = 0

#boolean array for each register to check data dependency
wait = [False for i in range(17)]

#variables referring about Branch.
branch_taken = 0
branch_target = ""

#clock cycles
cycles = 0

#Each iteration is clock-cycle.
while(True):
    cycles = cycles + 1
    
    ###################################### Releaving from stalls.
    if(raw and stall == 0):
        stage[0] = stage[1] = 1
        raw = 0
    if(cont and stall == 0):
        stage[0] = 1
        cont = 0
        
    ###################################### Stages execution
    """
    Each Stage corresponds to "IF statement".
    We update buffers and stage[] array (which tells which stage to execute in next cycle).
    Stall variable keep track of no.of cycles to be stalled.
    
    Special Functions at each stage:
    At InstructionDecode stage (stage 1), we detect data hazards
    At Decode stage we detect (stage 1), we detect control hazards
    At Execution stage, we decide branch_taken or not.
    At write-back stage we update wait[r1] = False indicating reg-r1 is available.
    """
    
    #write back stage.
    if(stage[4]):
        stage[4] = 0
        WriteBack(buff4[:4], buff4[4:8], LMD, buff4[8:16])

        if(int(buff4[:4],2) <= 8): wait[int(buff4[4:8],2)] = False

        #Halt Instruction
        if(buff4[:4] == "1111"):break
    
    #Memory Stage
    if(stage[3]):
        stage[3] = 0
        Opcode = buff3[:4]
        
        LMD = Memory(Opcode, buff3[4:8], ALUOutput)
        stage[4] = 1
        buff4 = buff3
    
    #Execute Stage
    if(stage[2]):
        stage[2] = 0
        ALUOutput, cond = Execute(opcode, A, B)
        stage[3] = 1
        buff3 = buff2 + ALUOutput
        
        #Indicating branch have to happen.
        if(cond or opcode == "1010"): 
            branch_taken = 1
            branch_target = ALUOutput

    #Decode Stage
    if(stage[1]):
        stage[1] = 0
        
        #return no.of stalls to incur if data hazard.
        x = data_hazard()
        if(x):
            stage[0] = 0
            raw = 1
            stall = x-1
            data_stalls += x
            stalls += x
            continue


        opcode, A, B = InstructionDecode()
        
        metric_typeInstruction(opcode)

        stage[2] = 1
        buff2 = buff1
        
        #updating wait[] array , indicating reg-r1 is not avaible.
        if(int(opcode,base = 2) <= 8): wait[int(IR[4:8], base = 2)] = True

        #control hazards for branch instructions (jmp , Beqz)
        if(opcode == "1010" or opcode == "1011"):
            stage[0] = 0
            stall = 2
            stalls += 2
            control_stalls += 2
            #metric
            cont = 1
            
        #instruction Fetch stage
        if(opcode == "1111"):
            stage[0] = 0
            continue

    if(stage[0]):
        InstructionFetch(branch_taken, branch_target)
        instructions += 1
        branch_taken = 0

        buff1 = IR[:8]
        stage[1] = 1
    

    ########## Decreasing stall if valid.
    if(stall > 0): stall -= 1
    ##########

#calculating CPI.
cpi = cycles/instructions
######################################## Writing into Files  ################################################


#writing dcache back into dcache.txt
f = open('dcache.txt', 'w')
for i in dcache:
    f.write( hex(int(i[0:4], base = 2))[2:] + hex(int(i[4:], base = 2))[2:]  )
    f.write('\n')
f.close()

#writing metrics - variables to output.txt 
f = open('output.txt', 'w')
f.write(f'instructions : {instructions}\n')
f.write(f'arthmetic_instructions : {arthmetic_instructions}\n')
f.write(f'logical_instructions : {logical_instructions}\n')
f.write(f'data_instructions : {data_instructions}\n')
f.write(f'control_instructions : {control_instructions}\n')
f.write(f'halt_instructions : {halt_instructions}\n')
f.write(f'cpi : {cpi}\n')
f.write(f'stalls : {stalls}\n')
f.write(f'data_stalls : {data_stalls}\n')
f.write(f'control_stalls : {control_stalls}\n')
f.close()

print("Output.txt File Created and dcache.txt updated!")

###################  END of file ############################################################################




