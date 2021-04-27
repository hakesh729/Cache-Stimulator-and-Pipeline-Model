"""
Authors : 
1. K Sathvik Joel CS19B025
2. P Cherrith CS19B035
3. D Hakesh CS19B017

Note : Require Python 2.7 or more version to run.

"""


import math

############# metric-variables ################################

instructions = 0
arthmetic_instructions = 0
logical_instructions = 0
data_instructions = 0
control_instructions = 0
halt_instructions = 0

cpi = 0

stalls = 0
data_stalls = 0
control_stalls = 0

################ global variables #############################
#store 8 bit information as strings (256 entries)
lcache = [] 
dcache = []

RF = [0,] #16 entries,8-bit each

PC = 0
IR = 0

#############################################################
#branch_taken = 0 or 1(int).branch_offset = 8 bit signed binary string.
#Note : branch_offset is in terms of no.of instructions (see readme.txt file given to us).
def InstructionFetch(branch_taken, branch_offset):

    #return nothing

def InstructionDecode():

    return opcode, R1, R2, R3, L1, A, B

def Execute(opcode, A, B):

    return ALUOutput, cond

def Memory(opcode, B):

    return data #in load instruction
    #return "" (empty string) if store

def WriteBack(R1, result):

    #return nothing

###############################################################
stage = [1,0,0,0,0]

#Tempory Registers used to store intermiedates.
A = B = ALUOutput = LMD = ""
cond = False

#IF [Buff1] ID [Buff2] EX [Buff3] Mem [Buff4] WB 

#Buffers between stages
buff1 = ""
buff2 = ""
buff3 = ""
buff4 = ""

#indicate type of stall
raw = con = unc = 0

#variables referring about Branch.
branch_taken = 0
branch_offset = ""

#clock cycles
cycles = 1

#Each iteration is clock-cycle.
while(cycles++):
    if(stage[4]):
        #indicate stage 4 is going to complete
        stage[4] = 0

        #R1 = register to which we have to write.
        R1 = buff4[4:8]

        WriteBack(R1,result)

        #emptying last buffer.
        buff4 = ""
        
        #Stall completion for "RAW" data hazard.
        if(raw): stage[0] = 1; stage[1] = 1; raw = 0; continue

    if(stage[3]):
        #indicate that stage[3] is going to complete
        stage[3] = 0

        #Getting corresponding relevant Opcode(different from opcode).
        #Either Load or store
        Opcode = buff3[:4]

        LMD = Memory(Opcode, buff3[8:16], ALUOutput)

        #if we performed "Load", we need to excute WB stage in next clock cycle.
        #otherwise no need.
        if(Opcode == "1000"):stage[4] = 1

        #Transferring buff3 to buff4
        buff4 = buff3

        if(con): stage[0] = 1; con = 0

    if(stage[2]):
        #Indicate that stage[3] is going to complete
        stage[2] = 0

        #ALU operation
        ALUOutput, cond = Execute(opcode, A, B)

        #if opcode is Memory-Instruction only,we need to execute stage-3 in next cycle.
        if(opcode == "1000" or opcode == "1001"): stage[3] = 1

        #transfering buff2 to buff3 without any updates.
        buff3 = buff2
        
        #if we incur "condition" for conditional branch  or Unconditional-branch ==> Branch is taken
        if(cond or unc): branch_taken = 1

        if(unc):stage[0] = 1; unc = 0;

    if(stage[1]):
        stage[1] = 0
        opcode, R1, R2, R3 , L , A, B = opInstructionDecode()
        stage[2] = 1
        buff2 = buff1 + B

        if(opcode == "1010"):stage[0] = 0; unc = 1; branch_offset = IR[4:12]
        if(opcode == "1011"):stage[0] = 0; con = 1

    if(stage[0]):
        x = data_hazard()
        InstructionFetch(branch_taken, branch_offset) 
        buff1 = IR[:8]
        stage[1] = 1
        if(x):
            stage[1] = 0
            stage[0] = 0
            raw = 1


#############################################################
#Read from lcache.txt to lcache[]


#Read from dcache.txt to dcache[]


#Read from RF.txt to RF[]


#writing dcache back into dcache.txt


#writing metrics - variables to output.txt 



###################  END of file ##################################
