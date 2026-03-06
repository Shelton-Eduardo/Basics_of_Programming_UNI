import collections

PAGE_SIZE = 4096

class Page:
    def __init__(self, vpn, data=None):
        self.vpn = vpn
        self.data = data if data else bytearray(PAGE_SIZE)
        self.is_dirty = False
        self.ref_bit = False

class MemoryManager:
    def __init__(self, ram_capacity):
        self.ram_capacity = ram_capacity
        self.physical_memory = []
        self.page_table = {}
        self.swap_space = {}
        self.clock_hand = 0

    def access(self, vpn, is_write=False):
        print(f"\nAccessing VPN {vpn} ({'WRITE' if is_write else 'READ'})...")
        
        # 1. Check if page is in physical memory
        page = self._find_in_ram(vpn)
        
        if page:
            print(f"-> Cache Hit!")
            page.ref_bit = True
            if is_write: page.is_dirty = True
            return page
        
        print(f"-> Page Fault!")
        return self._handle_page_fault(vpn, is_write)

    def _find_in_ram(self, vpn):
        for p in self.physical_memory:
            if p.vpn == vpn:
                return p
        return None

    def _handle_page_fault(self, vpn, is_write):
        if len(self.physical_memory) >= self.ram_capacity:
            self._evict_clock()
        
        # Load data from swap if exists, else new zeroed pag
        data = self.swap_space.pop(vpn, bytearray(PAGE_SIZE))
        new_page = Page(vpn, data)
        new_page.ref_bit = True
        new_page.is_dirty = is_write
        
        self.physical_memory.append(new_page)
        return new_page

    def _evict_clock(self):
        while True:
            victim = self.physical_memory[self.clock_hand]
            
            if not victim.ref_bit:
                print(f"-> Evicting VPN {victim.vpn}")
                evicted = self.physical_memory.pop(self.clock_hand)
                
                if evicted.is_dirty:
                    print(f"-> VPN {evicted.vpn} is dirty. Saving to SWAP.")
                    self.swap_space[evicted.vpn] = evicted.data
                
                # Fix clock
                if self.clock_hand >= len(self.physical_memory):
                    self.clock_hand = 0
                break
            else:
                victim.ref_bit = False
                self.clock_hand = (self.clock_hand + 1) % len(self.physical_memory)

# --- Verification Simulation ---
# Setup RAM with capacity for only 2 pages
# Theorethically, the one not called before should be set in memory whist the others remain in ram 
mmu = MemoryManager(ram_capacity=2)

mmu.access(vpn=101, is_write=True)
mmu.access(vpn=102, is_write=True)

mmu.access(vpn=101)

mmu.access(vpn=103, is_write=True)

mmu.access(vpn=102)





print("Hello Word")
