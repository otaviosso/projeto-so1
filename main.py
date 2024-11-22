import sys
import threading
import random
import queue
import time

t_0 = time.time()

S = int(sys.argv[1])  # pontos de distribuição
C = int(sys.argv[2])  # veículos
P = int(sys.argv[3])  # encomendas
A = int(sys.argv[4])  # quantidade máxima de encomendas por veículo

assert C < A, "C não é menor que A"
assert A < P, "A não é menor que P"

ships_queue = [queue.Queue() for _ in range(int(S))] # fila de encomendas por ponto de distribuição

remaining_shipments = P # variavel global que controla quantas encomendas faltam entregar, variavel usada pelo loop dos veiculos
remaining_shipments_lock = threading.Lock() # lock para modificar corretamente 

pontos_lock = [threading.Lock() for _ in range(int(S))] # uma lock por ponto
veiculos_queue = [queue.Queue(maxsize=A) for _ in range(int(C))] # fila de encomendas por veículo com tamanho maximo A em cada 

# inicializar arquivo com os logs
def log_file_initialize(encomenda,event_time):
    with open(f"shipment_{encomenda['id']}_trace.txt", "w") as f:
            f.write(f"Encomenda {encomenda['id']} criada\n")
            f.write(f"Origem: {encomenda['origem']}\n")
            f.write(f"Destino: {encomenda['destino']}\n")
            f.write(f"Horario de criacao: {event_time}\n")
            f.write("\n")

# salvar informações de carregamento/descarregamento de uma encomenda
def log_shipment_trace(encomenda, status, event_time, vehicle_id):
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
    
    # gerar ponto de início e de entrega
    start, dest = random.sample(range(0, int(S)), 2)

    # Criar e salvar encomenda
    encomenda = {"id": num, "origem": start, "destino": dest, "entregue": False}
    ships_queue[start].put(encomenda) # Encomenda é colocada na fila do seu ponto de origem
    print(f"Encomenda {num} adicionada ao ponto {start} para o destino {dest}")

    log_file_initialize(encomenda,time.time() - t_0) # anota as informações iniciais da encomenda

    while not encomenda["entregue"]: # encomenda fica dormindo enquanto nao for entregue
        time.sleep(1e-6)
    
    print(f"----- encomenda {num} entregue -----")
    with remaining_shipments_lock:
        remaining_shipments -= 1  # Garante que apenas uma thread modifique de cada vez


def fill_vehicle(start_pos, id):
    global ships_queue
    global veiculos_queue

    pos = start_pos
    temp_list = []
    with pontos_lock[pos]: # apenas o ponto atual é travado
        
        while not veiculos_queue[id].empty():# Verifica se o veiculo tem encomendas para serem entregues, se tiver, verifica cada uma e checa se o destino dela é o ponto atual
            encomenda = veiculos_queue[id].get()
            if encomenda["destino"] == pos:
                
                
                print(f"Veiculo {id} ENTREGANDO encomenda {encomenda['id']} no ponto {pos}")
                
                
                despacho_tempo = random.uniform(0.5, 2.0) # Tempo aleatorio de despacho
                time.sleep(despacho_tempo)
                
                encomenda["entregue"] = True  # Marca como entregue

                log_shipment_trace(encomenda, "unloaded",  time.time() - t_0, id) # Anota que a encomenda foi despachada
            else:
                temp_list.append(encomenda)  # Armazena encomendas que não foram entregues

        # Recoloca as encomendas que não foram entregues de volta na fila do veículo
        for encomenda in temp_list:
            veiculos_queue[id].put(encomenda)
        
        # Carrega novas encomendas para o veículo se ele tiver espaço
        while not veiculos_queue[id].full() and not ships_queue[pos].empty():
            encomenda = ships_queue[pos].get()
            veiculos_queue[id].put(encomenda)
            print(f"Veiculo {id} pegando encomenda {encomenda['id']} no ponto {pos}")
           
            log_shipment_trace(encomenda, "loaded",  time.time() - t_0, id)  # Anota tempo de carregar
    

def vehicle(i):
    global remaining_shipments
    num = i
    
    # gerar posição inicial
    start_pos = random.randint(0, int(S) - 1)
    print(f"Veiculo {num} posicao inicial {start_pos}")
    while remaining_shipments > 0: #Enquanto houver encomendas a serem entregues, viaja pro proximo ponto
        fill_vehicle(start_pos, num)
        travel_time = random.uniform(0.5, 2.0) # Tempo de viagem aleatorio 
        time.sleep(travel_time)
        start_pos = (start_pos + 1) % S # Avança pro proximo ponto na fila circular

# Imprime informações atuais de um ponto
def points_s(i):
    print(f"S:{i}")
    time.sleep(1)
    while not ships_queue[i].empty():
        time.sleep(1e-6)
    
    print(f"***** Todas encomendas do ponto {i} retiradas *****")


# Inicializa e inicia as threads
threads = []
for i in range(int(S)):
    thread = threading.Thread(target=points_s, args=(i,))
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