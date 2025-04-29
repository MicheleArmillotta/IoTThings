#include "crow.h"
#include <wiringPi.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <vector>
#include <mutex>

// Definizione del pin per il sensore di fiamma KY-026
constexpr int FLAME_SENSOR_PIN = 6;  // Cambia questo pin in base alla tua configurazione

// Struttura dati per memorizzare le rilevazioni della fiamma
class FlameDetector {
private:
    static constexpr size_t MAX_READINGS = 300;
    std::vector<bool> readings;
    mutable std::mutex readings_mutex;
    std::atomic<bool> running{false};
    std::thread sensor_thread;

public:
    FlameDetector() : readings(MAX_READINGS, false) {}

    ~FlameDetector() {
        stop();
    }

    // Avvia il thread di monitoraggio
    void start() {
        if (running) return;
        
        running = true;
        sensor_thread = std::thread([this]() {
            // Inizializzazione wiringPi
            if (wiringPiSetupGpio() == -1) {
                std::cerr << "Errore nell'inizializzazione di wiringPi!" << std::endl;
                running = false;
                return;
            }
            
            // Configurazione pin
            pinMode(FLAME_SENSOR_PIN, INPUT);
            
            std::cout << "Monitoraggio del sensore di fiamma avviato..." << std::endl;
            
            while (running) {
                // La lettura del sensore - LOW (0) quando non c'è fiamma, HIGH (1) quando rileva fiamma
                bool flame_detected = (digitalRead(FLAME_SENSOR_PIN) == HIGH);
                
                // Aggiunta della nuova rilevazione
                {
                    std::lock_guard<std::mutex> lock(readings_mutex);
                    readings.push_back(flame_detected);
                    if (readings.size() > MAX_READINGS) {
                        readings.erase(readings.begin());
                    }
                    
                    if (flame_detected) {
                        std::cout << "Rilevata fiamma!" << std::endl;
                    }
                }
                
                // Breve pausa tra le letture
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        });
    }
    
    // Ferma il thread di monitoraggio
    void stop() {
        if (!running) return;
        
        running = false;
        if (sensor_thread.joinable()) {
            sensor_thread.join();
        }
    }
    
    // Verifica se è stata rilevata una fiamma nelle ultime MAX_READINGS letture
    bool was_flame_detected() const {
        std::lock_guard<std::mutex> lock(readings_mutex);
        
        for (const auto& reading : readings) {
            if (reading) {
                return true;  // Se anche solo una lettura ha rilevato fiamma, ritorna true
            }
        }
        
        return false;  // Nessuna fiamma rilevata
    }
};

int main() {
    // Istanza del rilevatore di fiamma
    FlameDetector detector;
    
    // Avvio del monitoraggio del sensore
    detector.start();
    
    // Setup dell'applicazione Crow
    crow::SimpleApp app;
    
    // API endpoint per verificare se è stata rilevata una fiamma
    CROW_ROUTE(app, "/flame_status")
    ([&detector]() {
        crow::json::wvalue response;
        response["flame_detected"] = detector.was_flame_detected();
        return response;
    });
    
    // Avvio del server
    std::cout << "Server avviato sulla porta 18080..." << std::endl;
    app.port(18083).multithreaded().run();
    
    // Ferma il detector quando il programma termina
    detector.stop();
    
    return 0;
}
