import RPi.GPIO as GPIO
import time
from threading import Thread, Event
import statistics
from flask import Flask, jsonify, request
from flask_cors import CORS


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LED_VERDE = 12  
LED_ROSSO = 25  
PB1 = 13        
PB2 = 26


GPIO.setup(LED_VERDE, GPIO.OUT)
GPIO.setup(LED_ROSSO, GPIO.OUT)
GPIO.setup(PB1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PB2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

modalita_play = True  
tempo_bpm = 0         
tap_tempi = []        
ultimo_tap = 0     
intervallo_sec = 0    
stop_event = Event()  
bpms = []


app = Flask(__name__)
CORS(app)

def deleteValue(arr, val):
    """Modifica l'array in-place sostituendo tutte le occorrenze di val con 0."""
    for i in range(len(arr)):
        if arr[i] == val:
            arr[i] = 0
            
def defineMin(arr):
    """Trova il bpm minimo > 0."""
    minimo = 10000
    
    for i in range(len(arr)):
        if arr[i] < minimo and arr[i]!=0 :
            minimo= arr[i]
    return minimo

def calcola_bpm():
    """Calcola i BPM dai tempi di tap memorizzati"""
    global intervallo_sec
    
    if len(tap_tempi) < 4:
        return 0  

    differenze = []
    for i in range(1, len(tap_tempi)):
        differenze.append(tap_tempi[i] - tap_tempi[i-1])
    

    media_differenze = statistics.mean(differenze)
    
 
    bpm = 60 / media_differenze if media_differenze > 0 else 0
    
    intervallo_sec = 60 / bpm if bpm > 0 else 0
    
    return int(bpm)

def lampeggia_led():
    """Funzione per lampeggiare il LED verde al ritmo impostato"""
    while not stop_event.is_set():
        if modalita_play and intervallo_sec > 0:
            GPIO.output(LED_VERDE, GPIO.HIGH)
            time.sleep(0.1)  
            GPIO.output(LED_VERDE, GPIO.LOW)
            
           
            tempo_attesa = intervallo_sec - 0.1
            if tempo_attesa > 0:
                time.sleep(tempo_attesa)
        else:
           
            GPIO.output(LED_VERDE, GPIO.LOW)
            time.sleep(0.1)  
def gestisci_pulsante_tap(canale):
    """Gestisce la pressione del pulsante di tap (PB1)"""
    global ultimo_tap
    
   
    if not modalita_play:
        GPIO.output(LED_ROSSO, GPIO.HIGH)
        tempo_corrente = time.time()
        
        tap_tempi.append(tempo_corrente)
        ultimo_tap = tempo_corrente
        
        time.sleep(0.1)
        GPIO.output(LED_ROSSO, GPIO.LOW)

def gestisci_cambio_modalita(canale):
    """Gestisce il cambio di modalitÃ  (PB2)"""
    global modalita_play, tempo_bpm, tap_tempi
    
    time.sleep(0.2)
    
    modalita_play = not modalita_play
    
    if modalita_play:
        print("ModalitÃ : PLAY")
        GPIO.output(LED_ROSSO, GPIO.LOW)
        
        if len(tap_tempi) >= 4:
            tempo_bpm = calcola_bpm()
            bpms.append(tempo_bpm)
            print(f"Nuovo tempo impostato: {tempo_bpm} BPM")
        else:
            print("Non abbastanza tap per calcolare il BPM. Rimango al tempo precedente.")
        
        tap_tempi = []
    else:
        print("ModalitÃ : LEARN")
        GPIO.output(LED_VERDE, GPIO.LOW)
        tap_tempi = []  

@app.route('/bpm', methods=['GET', 'POST'])
def bpm():
    """Gestisce sia il GET che il POST per il BPM"""
    global tempo_bpm, intervallo_sec

    if request.method == 'GET':
        return jsonify({"bpm": tempo_bpm})

    elif request.method == 'POST':
        data = request.get_json()
        if "bpm" in data and isinstance(data["bpm"], (int, float)) and data["bpm"] > 0:
            tempo_bpm = int(data["bpm"])
            bpms.append(tempo_bpm)
            intervallo_sec = 60 / tempo_bpm
            return jsonify({"message": f"BPM impostato a {tempo_bpm}"}), 200
        else:
            return jsonify({"error": "Valore BPM non valido"}), 400
        
@app.route('/bpm/max', methods=['GET', 'DELETE'])
def bpm_max():
    """Gestisce sia il GET che il DELETE per il BPM massimo"""
    global massimo
    massimo=max(bpms)
        
    if request.method == 'GET':
        return jsonify({"bpm": massimo})
        
    elif request.method == 'DELETE':
            deleteValue(bpms,massimo)
            return jsonify({"message": f"Massimo({massimo} BPM) eliminato con successo"}),200
            
    
@app.route('/bpm/min', methods=['GET', 'DELETE'])
def bpm_mim():
    """Gestisce sia il GET che il DELETE per il BPM massimo"""
    global minimo
    minimo=defineMin(bpms)
        
    if request.method == 'GET':
        return jsonify({"bpm": minimo})
        
    elif request.method == 'DELETE':
            deleteValue(bpms,minimo)
            return jsonify({"message": f"Minimo ({minimo} BPM)eliminato con successo"}),200
            
def start_flask():
    """Avvia il server Flask"""
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)



GPIO.add_event_detect(PB1, GPIO.FALLING, callback=gestisci_pulsante_tap, bouncetime=100)
GPIO.add_event_detect(PB2, GPIO.FALLING, callback=gestisci_cambio_modalita, bouncetime=300)

thread_lampeggiamento = Thread(target=lampeggia_led)
thread_lampeggiamento.daemon = True
thread_lampeggiamento.start()

thread_flask = Thread(target=start_flask)
thread_flask.daemon = True
thread_flask.start()

print("Metronomo avviato in modalitÃ  PLAY")
print("Premere il pulsante PB2 per passare alla modalitÃ  LEARN")
print("In modalitÃ  LEARN, usa PB1 per impostare il tempo (minimo 4 tap)")
print("Premere Ctrl+C per uscire")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    stop_event.set()
    thread_lampeggiamento.join(timeout=1)
    GPIO.cleanup()
    print("\nProgramma terminato")