#Author : D Hakesh
import math
import random

#########################################################################
#########################################################################

def binTodec(x):
    ans = 0
    p = 1
    for i in x[::-1]:
        if(i == '1'): ans += p
        p *= 2
    return ans


class perf_counters:
    def __init__(self,associativity , replacement_policy ):
        self.cache_access = 0
        self.read_access = 0
        self.write_access = 0
        self.cache_miss = 0
        self.compulsory_miss = 0
        self.capacity_miss = 0
        self.conflict_miss = 0
        self.read_miss = 0
        self.write_miss = 0
        self.dirty_evicted = 0

    def update(self, strings):
        self.__dict__[strings] += 1
            
    def print_metrics(self):
        for k,v in self.__dict__.items():
            print( k ," = ", v)    

class cacheBlock:
    def __init__(self,tag,v_bit,d_bit,next):
        self.tag = tag
        self.dirty_bit = d_bit
        self.valid_bit = v_bit
        self.next_block = next
        

class cache:
    #defined only for 31-bit memory references
    def __init__(self, associativity, replacement_policy, cache_size, block_size, addr_length):
        self.metrics = perf_counters()

        self.associativity = associativity
        self.size = cache_size
        self.block_size = block_size
        
        

        self.num_blocks = cache_size // block_size
        if(associativity == 0):
            self.num_sets = 1
            self.num_ways = self.num_blocks
        else:
            self.num_sets = (self.num_blocks)//associativity
            self.num_ways = associativity

        #assigning replacement policy        
        if(replacement_policy == 0): self.replacement_policy = random_replacer(self.num_sets, self.num_ways)
        elif(replacement_policy == 1):self.replacement_policy = lru_replacer(self.num_sets, self.num_ways)    
        else:self.replacement_policy = pseudo_lru_replacer(self.num_sets, self.num_ways)

        self.addr_length = addr_length
        self.offset_size = int(math.log2(block_size))
        self.setIndex_size = int(math.log2(self.num_blocks))
        self.tag_size = addr_length - self.offset_size - self.setIndex_size

        #initialzing cache with invalid blocks(empty blocks)
        #we deal only with tag-self.array
        self.tag_self.array = [[cacheBlock('',0,0,None) for i in range(self.num_ways)] for j in range(self.num_sets) ]
        #linking the cache blocks
        for i in range(self.num_sets):
            prev = self.tag_self.array[i][0]
            for j in range(1,self.num_ways):
                prev.next_block = self.tag_self.array[i][j]
                prev = self.tag_self.array[i][j]

    def access(self,addr,access_type):
        #0 for read and 1 for write
        self.access_type = access_type

        #updating metrics of cache
        self.metrics.cache_access += 1
        self.metrics.read_access += (1 - access_type)
        self.metrics.write_access += access_type

        #dividing address
        self.curr_set = binTodec(addr[self.tag_size:self.addr_length -self.offset_size])
        self.curr_tag = addr[0:self.tag_size]

        #calling comparator
        comparator()

        if(self.hit_status == 1):
            self.replacement_policy.update(self.curr_set, self.curr_tag)
            return

        #Miss case
        if(self.valid_set == 0):
            replace_invalid()
            self.replacement_policy.replace(self.curr_set, self.curr_tag)
            self.metrics.compulsory_miss += 1



    def comparator(self):
        self.valid_set = 1
        self.hit_status = 0

        block = tag_self.array[self.curr_set][0]
        while(block != None):
            if(block.valid_bit == 0) : self.valid_set = 0
            if(block.tag == self.curr_tag):self.hit_status = 1  
            block = block.next_block
    
    def replace_invalid(self):

    def eviction(self):

#############################################
#Return way number to be evicted
#Note : other replacement policies give tag number
class random_replacer:
    def __init__(self, way_num):
        self.max_number = way_num

    def update(self, dummy, dummy): pass

    def replace(self,dummy, dummy):
        return random.randint(0, self.way_num)
    
##################################################
#Return Tag while replacement
class lru_replacer:
    #Linked-List node for LRU Policy implementation
    class lru_node:
        def __init__(self, tag, next): self.tag = tag; self.next = next

    def __init__(self, num_sets, num_ways):
        self.rows = num_sets
        self.row_size = num_ways
        self.array = [[lru_node("", None)] for j in range(num_sets)]

        #linking 
        for i in range(self.rows):
            prev = self.tag_self.array[i][0]
            for j in range(1,self.row_size):
                prev.next = self.array[i][j]
                prev = self.tag_self.array[i][j]

    
    def update(self, set_num, tag):
        #Search for tag
        if(self.array[set_num] == None): print("Error : Data Not in LRU - Cant Update"); exit(0)
        temp = self.array[set_num]

        #case where No need of update
        if(temp.tag == tag): return 

        new_head = None
        while(temp.next != None):
            if(temp.next.tag == tag):
                new_head = temp.next
                temp.next = temp.next.next
                break
            temp = temp.next
        
        if(new_head == None):print("Error : Data Not in LRU - Cant Update"); exit(0)

        #Moving recently accessed element to Front
        new_head.next = self.array[set_num]
        self.array[set_num] = new_head

    def replace(self , set_num , tag):
        if(self.array[set_num] == None):print("Error : No Data in LRU to replacement tag");exit(0)

        #Adding new node at head
        self.array[set_num] = lru_node(tag, self.array[set_num])

        #Deleting Last Node (least Recently Accessed Node)
        temp = self.array[set_num]
        while(temp.next.next != None): temp = temp.next
        replaced_tag = temp.next.tag
        temp.next = None

        return replaced_tag

#################################################################

class pseudo_lru_replacer:
    def __init__(self, num_sets, num_ways):
        self.rows = num_sets
        self.row_size = 2 * num_ways - 1
        
        #self.array representation of tree and Initialization
        self.tree =  [[0 for i in range(self.row_size)] for j in range(self.rows)]

        #Index in tree where leafs (tags) start.
        self.leaf_start = num_ways - 1

    def update(self , set_num , tag):
        pos = 0
        for i in range( self.leaf_start, self.row_size):
            if( self.tree[set_num][i] == tag ):
                pos = i
                break
        if(pos == 0):print("Error : No Data in LRU to replacement tag");exit(0)

        while( pos != 0 ):
            d = (pos - 1)//2
            #Toggling the bit if it is pointing to same sub - tree.
            self.tree[set_num][d] ^= ((pos %2) ^ self.tree[set_num][d])
            pos = d
        
    def replace(self, set_num , tag):
        pos= 0
        while( pos < self.leaf_start):
            d = self.tree[set_num][pos]
            self.tree[set_num][pos] ^= 1
            pos = 2*pos + (d+1)
        replaced_tag = self.tree[set_num][pos]
        #replacement
        self.tree[set_num][pos] = tag

        return replaced_tag
