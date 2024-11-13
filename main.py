import sys
import threading
import random
import queue
import time

t_0 = time.time()

S = 5  # distribution points
C = 3  # vehicles
P = 15  # shipments
A = 4  # max shipments per vehicle

assert C < A, "C is not lesser than A"
assert A < P, "A is not lesser than P"

ships_queue = [queue.Queue() for _ in range(int(S))]

remaining_shipments = P
remaining_shipments_lock = threading.Lock()

pontos_lock = [threading.Lock() for _ in range(int(S))]
veiculos_queue = [queue.Queue(maxsize=A) for _ in range(int(C))]

def log_file_inicialize(encomenda,event_time):
    with open(f"shipment_{encomenda['id']}_trace.txt", "w") as f:
            f.write(f"Encomenda {encomenda['id']} criada\n")
            f.write(f"Origem: {encomenda['origem']}\n")
            f.write(f"Destino: {encomenda['destino']}\n")
            f.write(f"Horario de criacao: {event_time}\n")
            f.write("\n")

def log_shipment_trace(encomenda, status, event_time, vehicle_id=None):
    """Log shipment information to a file."""
    with open(f"shipment_{encomenda['id']}_trace.txt", "a") as f:
        if status == "loaded":
            f.write(f"Carregada no veiculo {vehicle_id} no horario: {event_time}\n")
        elif status == "unloaded":
            f.write(f"Descarregada pelo veiculo {vehicle_id} no horario: {event_time}\n")
        f.write("\n")


def shipment(i):
    
    global ships_queue
    global remaining_shipments
    num = i
    
    # generate starting point and destination
    start = random.randint(0, int(S) - 1)
    
    dest = random.randint(0, int(S) - 1)
    while dest == start:
        dest = random.randint(0, int(S) - 1)

    # Create and log shipment
    encomenda = {"id": num, "origem": start, "destino": dest, "entregue": False}
    ships_queue[start].put(encomenda)
    print(f"Encomenda {num} adicionada ao ponto {start} para o destino {dest}")

    log_file_inicialize(encomenda,time.time() - t_0)

    while not encomenda["entregue"]:
        time.sleep(1e-6)
    
    print(f"----- encomenda {num} entregue -----")
    with remaining_shipments_lock:
        remaining_shipments -= 1  # Garante que apenas uma thread modifica de cada vez


def fill_vehicle(start_pos, id):
    global ships_queue
    global veiculos_queue

    pos = start_pos
    temp_list = []
    with pontos_lock[pos]:
        # Carrega ou descarrega encomendas do veículo
        while not veiculos_queue[id].empty():
            encomenda = veiculos_queue[id].get()
            if encomenda["destino"] == pos:
                # Log unloading time
                
                print(f"Veiculo {id} ENTREGANDO encomenda {encomenda['id']} no ponto {pos}")
                
                
                despacho_tempo = random.uniform(0.5, 2.0)
                time.sleep(despacho_tempo)
                
                encomenda["entregue"] = True  # Marca como entregue

                log_shipment_trace(encomenda, "unloaded",  time.time() - t_0, id)
            else:
                temp_list.append(encomenda)  # Armazena encomendas que não foram entregues

        # Recoloca as encomendas que não foram entregues de volta na fila do veículo
        for encomenda in temp_list:
            veiculos_queue[id].put(encomenda)
        
        # Carrega novas encomendas para o veículo
        while not veiculos_queue[id].full() and not ships_queue[pos].empty():
            encomenda = ships_queue[pos].get()
            veiculos_queue[id].put(encomenda)
            print(f"Veiculo {id} pegando encomenda {encomenda['id']} no ponto {pos}")
           
            log_shipment_trace(encomenda, "loaded",  time.time() - t_0, id)  # Log loading time
    

def vehicle(i):
    global remaining_shipments
    num = i
    
    # generate starting position
    start_pos = random.randint(0, int(S) - 1)
    while remaining_shipments > 0:
        fill_vehicle(start_pos, num)
        travel_time = random.uniform(0.5, 2.0)
        time.sleep(travel_time)
        start_pos = (start_pos + 1) % S


def print_S(i):
    print(f"S:{i}")
    time.sleep(1)
    while not ships_queue[i].empty():
        time.sleep(1e-6)
    
    print(f"***** Todas encomendas do ponto {i} retiradas *****")


# Inicializa e inicia as threads
threads = []
for i in range(int(S)):
    thread = threading.Thread(target=print_S, args=(i,))
    threads.append(thread)
    thread.start()

for i in range(int(P)):
    thread = threading.Thread(target=shipment, args=(i,))
    threads.append(thread)
    thread.start()

for i in range(int(C)):
    thread = threading.Thread(target=vehicle, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
