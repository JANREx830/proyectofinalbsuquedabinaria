import multiprocessing
import time
import random
def busqueda_binaria_paralela(sub_lista, elemento_a_buscar, cola_resultados, indice_inicio):
    #Realiza una búsqueda binaria en una sub-lista y pone el resultado en una cola.
    inicio = 0
    fin = len(sub_lista) - 1 
    while inicio <= fin:
        medio = (inicio + fin) // 2
        if sub_lista[medio] == elemento_a_buscar:
            # Se encontró el elemento, se coloca el índice global en la cola
            cola_resultados.put(indice_inicio + medio)
            return
        elif sub_lista[medio] < elemento_a_buscar:
            inicio = medio + 1
        else:
            fin = medio - 1
    # Si el bucle termina, el elemento no está en esta sub-lista
    return
if __name__ == "__main__":
    # --- Configuración del Experimento ---
    TAMANO_LISTA = 200_000_000
    ELEMENTO_A_BUSCAR = 150_876_345
    NUM_PROCESOS = multiprocessing.cpu_count() # Usar todos los núcleos disponibles
    print(f"--- Búsqueda Binaria Paralela con {NUM_PROCESOS} procesos ---")
    print(f"Tamaño de la lista: {TAMANO_LISTA}")
    print(f"Elemento a buscar: {ELEMENTO_A_BUSCAR}\n")
    # --- Generación de Datos ---
    print("Generando lista ordenada de gran tamaño...")
    lista_grande = list(range(TAMANO_LISTA))
    print("Lista generada.\n")

    # --- Ejecución Paralela ---
    cola_resultados = multiprocessing.Queue()
    procesos = [] 
    tamano_segmento = TAMANO_LISTA // NUM_PROCESOS 
    print(f"Iniciando búsqueda con {NUM_PROCESOS} procesos...")
    tiempo_inicio_paralelo = time.time()
    for i in range(NUM_PROCESOS):
        indice_inicio = i * tamano_segmento 
        # Asegurar que el último proceso cubra hasta el final de la lista
        if i == NUM_PROCESOS - 1:
            indice_fin = TAMANO_LISTA
        else:
            indice_fin = indice_inicio + tamano_segmento 
        sub_lista = lista_grande[indice_inicio:indice_fin]
        
        proceso = multiprocessing.Process(
            target=busqueda_binaria_paralela,
            args=(sub_lista, ELEMENTO_A_BUSCAR, cola_resultados, indice_inicio)
        )
        procesos.append(proceso)
        proceso.start()
    # Esperar a que al menos un proceso encuentre el resultado
    try:
        resultado = cola_resultados.get(timeout=30) # Espera máximo 30 segundos
        encontrado = True
    except queue.Empty:
        resultado = -1
        encontrado = False
    # Terminar todos los procesos una vez que se ha encontrado el resultado o ha expirado el tiempo
    for proceso in procesos:
        proceso.terminate()
        proceso.join()
        
    tiempo_fin_paralelo = time.time()
    duracion_paralela = tiempo_fin_paralelo - tiempo_inicio_paralelo
    print("\n--- Resultados de la Búsqueda Paralela ---")
    if encontrado:
        print(f"Elemento {ELEMENTO_A_BUSCAR} encontrado en el índice: {resultado}")
    else:
        print(f"Elemento {ELEMENTO_A_BUSCAR} no encontrado en la lista.")
    print(f"Tiempo de ejecución paralelo: {duracion_paralela:.6f} segundos.")
    # --- Ejecución Secuencial para Comparación ---
    print("\n--- Comparando con Búsqueda Binaria Secuencial ---")
    tiempo_inicio_secuencial = time.time()
    # Simulación de búsqueda binaria secuencial (sin el overhead de la función)
    inicio_s, fin_s = 0, len(lista_grande) - 1
    resultado_secuencial = -1
    while inicio_s <= fin_s:
        medio_s = (inicio_s + fin_s) // 2
        if lista_grande[medio_s] == ELEMENTO_A_BUSCAR:
            resultado_secuencial = medio_s
            break
        elif lista_grande[medio_s] < ELEMENTO_A_BUSCAR:
            inicio_s = medio_s + 1
        else:
            fin_s = medio_s - 1
    tiempo_fin_secuencial = time.time()
    duracion_secuencial = tiempo_fin_secuencial - tiempo_inicio_secuencial
    print(f"Elemento encontrado en el índice: {resultado_secuencial}")
    print(f"Tiempo de ejecución secuencial: {duracion_secuencial:.6f} segundos.")
    # --- Cálculo de la Mejora (Speedup) ---
    if duracion_paralela > 0:
        speedup = duracion_secuencial / duracion_paralela
        print(f"\nMejora (Speedup): {speedup:.2f}x")
