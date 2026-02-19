import random

class ToricSimulator:
    def __init__(self, L):
        self.L = L

        self.support = [[0 for _ in range(L)] for _ in range (L)]
        self.qubits = [[0 for _ in range(L)] for _ in range (L*2)]
        self.vertices = []

        #union find things
        self.is_syndrome = [0 for _ in range(2*L*L)]
        self.display_syndrome = []
        self.parent = [x for x in range(2*L*L)]
        self.size = [1 for x in range(2*L*L)]
        self.parity = [0 for x in range(2*L*L)]
        self.clusters = []
        self.boundaries = {}
        self.edges = [0 for x in range(2*L*L)]
        self.tree = [0 for x in range(2*L*L)]
        self.leaves = {}
        self.got_leaves = False
        self.updated = True


    
    def add_error(self, error_rate):
        self.error_rate = error_rate
        for i in range(self.L*2):
            for j in range(self.L):
                if (random.random() < error_rate):
                    self.qubits[i][j] = 1
    
    def get_syndromes(self):
        self.clusters = []
        for y in range(self.L):
            for x in range(self.L):
                p1 = [x, y*2]

                p2 = [x-1, y*2]
                if (p2[0] < 0):
                    p2[0] = self.L-1

                p3 = [x, y*2+1]
                if (p3[1] >= self.L*2):
                    p3[1] = 0
                
                p4 = [x, y*2-1]
                if (p4[1] < 0):
                    p4[1] = self.L*2-1
                
                
                parity = (self.qubits[p1[1]][p1[0]] + 
                          self.qubits[p2[1]][p2[0]] + 
                          self.qubits[p3[1]][p3[0]] + 
                          self.qubits[p4[1]][p4[0]])
                if (parity == 1):
                    self.is_syndrome[self.L*y + x] = 1
                    self.parity[self.L*y + x] = 1
                    self.clusters.append(self.L*y + x)
                    self.boundaries[self.L*y + x] = [self.L*y + x]
        
        self.display_syndrome = list(self.is_syndrome)
    
    def display(self):
        print("Raw qubits: ")
        for x in range(self.L*2):
            print(self.qubits[x])
        print("Syndromes: ")
        print(self.is_syndrome)
        
        for y in range(0, self.L*2, 2):
            for x in range(self.L):
                vertex = '-'
                if (self.is_syndrome[int(y/2)*self.L + x] == 1):
                    vertex = 'X'
                print(f"{vertex}--{self.qubits[y][x]}--", end='')
            print("")
            for x in range(self.L):
                print("|     ", end='')
            print("")
            for x in range(self.L):
                print(f"{self.qubits[y+1][x]}     ", end='')
            print("")
            for x in range(self.L):
                print("|     ", end='')
            print("")

    def get_neighbors(self, i):
        n = []
        x = i % self.L
        y = i // self.L

        p1 = [x, y*2]

        p2 = [x-1, y*2]
        if (p2[0] < 0):
            p2[0] = self.L-1

        p3 = [x, y*2+1]
        if (p3[1] >= self.L*2):
            p3[1] = 0
        
        p4 = [x, y*2-1]
        if (p4[1] < 0):
            p4[1] = self.L*2-1
        
        n1 = [x+1, y]
        if (n1[0] >= self.L):
            n1[0] = 0
        
        n2 = [x-1, y]
        if (n2[0] < 0):
            n2[0] = self.L - 1
        
        n3 = [x, y+1]
        if (n3[1] >= self.L):
            n3[1] = 0
        
        n4 = [x, y-1]
        if (n4[1] < 0):
            n4[1] = self.L - 1
        
        return [[p1[1]*self.L + p1[0], n1[1]*self.L + n1[0]],
                [p2[1]*self.L + p2[0], n2[1]*self.L + n2[0]],
                [p3[1]*self.L + p3[0], n3[1]*self.L + n3[0]],
                [p4[1]*self.L + p4[0], n4[1]*self.L + n4[0]],]
        

    def find(self, i):
        node = i
        while (self.parent[node] != node):
            node = self.parent[node]
        
        parent = node
        node = i

        while (self.parent[node] != node):
            temp = self.parent[node]
            self.parent[node] = parent
            node = temp
        
        return parent

    def union(self, i, j):
        if self.find(i) == self.find(j):
            return
        if self.size[self.find(i)] < self.size[self.find(j)]:
            temp = i
            i = j
            j = temp
        
        g1 = self.find(i)
        g2 = self.find(j)

        if g2 in self.boundaries.keys():
            self.boundaries[g1] += self.boundaries[g2]
            del self.boundaries[g2]
        
        self.size[g1] += self.size[g2]
        self.parity[g1] = (self.parity[g1] + self.parity[g2]) % 2
        self.parent[g2] = g1
        if g2 in self.clusters:
            self.clusters.remove(g2)
        if j in self.clusters:
            self.clusters.remove(j)

    def iterate(self):
        updated = False
        for cluster in self.clusters:
            if (self.parity[cluster] == 1):
                for v in list(self.boundaries[cluster]):
                    neighbors = self.get_neighbors(v)

                    #experimental
                    full_edges = 0
                    for edge in neighbors:
                        if (self.edges[edge[0]] < 2):
                            self.edges[edge[0]] += 1
                            updated = True
                            if (self.edges[edge[0]] == 2):
                                if (self.find(v) != self.find(edge[1])):
                                    self.edges[edge[0]] = 3
                                self.union(self.find(v), self.find(edge[1]))
                                full_edges += 1
                                if cluster in self.boundaries.keys() and self.size[self.find(edge[1])] == 1:
                                    self.boundaries[cluster].append(edge[1])
                        else:
                            full_edges += 1
                    
                    if (full_edges >= 4 and cluster in self.boundaries and v in self.boundaries[cluster]):
                        self.boundaries[cluster].remove(v)
        if (not updated):
            self.updated = False

    
    def peel(self):
        if (not self.got_leaves):
            self.get_leaves()
            self.got_leaves = True
        for cluster in self.clusters:
            for v in list(self.leaves[cluster]):
                #if self.is_leaf(v):
                neighbors = self.get_neighbors(v)

                for n in neighbors:
                    if (self.edges[n[0]] == 3):
                        if (self.is_syndrome[v]):
                            self.is_syndrome[n[1]] ^= 1
                            self.is_syndrome[v] ^= 1
                            self.edges[n[0]] = 0
                            self.tree[n[0]] = 4
                        else:
                            self.edges[n[0]] = 0
                    else:
                        self.edges[n[0]] = 0
                    if self.is_leaf(n[1]) and n[1] not in self.leaves[cluster]:
                        self.leaves[cluster].append(n[1])
                    
                if v in self.leaves[cluster]:
                    self.leaves[cluster].remove(v)

    def is_leaf(self, i):
        neighbors = self.get_neighbors(i)

        count = 0
        for n in neighbors:
            if (self.edges[n[0]] == 3):
                count += 1
        
        return count == 1
    
    def get_leaves(self):
        for x in range(self.L*self.L):
            if self.is_leaf(x):
                if self.find(x) in self.leaves.keys():
                    self.leaves[self.find(x)].append(x)
                else:
                    self.leaves[self.find(x)] = [x]
    
    def has_odd(self):
        if not self.updated:
            return False
        for x in self.clusters:
            if self.parity[self.find(x)] == 1:
                return True
        return False
    
    def display2(self):
        print("\n ------------------------------- \n\n")
        for y in range(0, self.L*2, 2):
            for x in range(self.L):
                vertex = self.find(int(y/2)*self.L + x) % 10
                print(f"{vertex}--{self.edges[y*self.L + x]}--", end='')
            print("")
            for x in range(self.L):
                print("|     ", end='')
            print("")
            for x in range(self.L):
                print(f"{self.edges[(y+1)*self.L + x]}     ", end='')
            print("")
            for x in range(self.L):
                print("|     ", end='')
            print("")