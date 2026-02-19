from toric_simulator import ToricSimulator

toric = ToricSimulator(5)
toric.add_error(0.05)
toric.get_syndromes()
toric.display()
toric.display2()
while toric.has_odd():
    toric.iterate()
    toric.display2()
    input()

print("Done grouping, starting to peel")
while not toric.has_odd():
    toric.peel()
    toric.display2()
    input()

print("Done peeling")