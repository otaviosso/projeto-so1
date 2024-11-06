import sys
import threading
import random
import queue

transport_mutex = threading.Lock()

S = sys.argv[1] # dist points
C = sys.argv[2] # vehicles
P = sys.argv[3] # shipments
A = sys.argv[4]

assert C < A, "C is not lesser than A"
assert A < P, "A is not lesser than P"

#   S0 S1 S2 ... each column is a distribution point
# P0
# P1
# P2
# .
# .
# .
# each row is a shipment
ships = [[0] * int(S) for _ in range(int(P))] # each distribution point has a shipment queue
ships_queue = [queue.Queue() for _ in range(int(S))]

points = [0] * int(S)
remaining_shipments = P

def shipment(i):
    num = i
    
    # generate starting point and destination
    start = random.randint(0, int(S) - 1)
    ships[num][start] += 1
    dest = random.randint(0, int(S) - 1)
    while(dest == start):
        dest = random.randint(0, int(S) - 1)
    info = {"dest": dest}
    ships_queue[start].put(info)
    print(f"P:{num} start:{start} destination:{dest}")

def fill_vehicle(start_pos, cargo):
    pos = start_pos
    
    transport_mutex.acquire()
    while()
    
    
def vehicle(i):
    num = i
    
    # generate starting position
    start_pos = random.randint(0, int(S) - 1)
    
    cargo = []
    fill_vehicle(start_pos, cargo)
    # check if shipment queue at pos is not empty
    emp_queue = True
    while(emp_queue):
        pos = random.randint(0, int(S) - 1)
        for i in range(int(P)):
            if (ships[i][pos] != 0):
                emp_queue = False
                break
    
    print(f"vehicle:{num} pos:{pos}")
    
def print_S(i):
    num = i
    
    print(f"S:{num}")

threads = []
for i in range(int(P)):
    thread = threading.Thread(target=shipment, args = (i,))
    threads.append(thread)
    thread.start()

for i in range(int(C)):
    thread = threading.Thread(target=vehicle, args = (i,))
    threads.append(thread)
    thread.start()
    
for i in range(int(S)):
    thread = threading.Thread(target=print_S, args = (i,))
    threads.append(thread)
    thread.start()
    
for thread in threads:
    thread.join()
    
for i in range(int(P)):
    for j in range(int(S)):
        print(ships[i][j], end = " ")
    print()