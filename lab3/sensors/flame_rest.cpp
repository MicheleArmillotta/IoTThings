#include "crow.h"
#include <wiringPi.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <vector>
#include <mutex>

// Pin definition for KY-026 flame sensor
constexpr int FLAME_SENSOR_PIN = 6;  // Cambia questo pin in base alla tua configurazione

// Data structure to store flame readings
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

    // Start the monitoring thread
    void start() {
        if (running) return;
        
        running = true;
        sensor_thread = std::thread([this]() {
           // Initialize wiringPi
            if (wiringPiSetupGpio() == -1) {
                std::cerr << "Errore nell'inizializzazione di wiringPi!" << std::endl;
                running = false;
                return;
            }
            
            // Pin configuration
            pinMode(FLAME_SENSOR_PIN, INPUT);
            
            std::cout << "Flame sensor monitoring started..." << std::endl;
            
            while (running) {
                // Sensor reading - LOW (0) when there is no flame, HIGH (1) when it detects flame
                bool flame_detected = (digitalRead(FLAME_SENSOR_PIN) == HIGH);
                
                // Adding new detection
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
                
               // Short break between readings
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        });
    }
    
    // Stop the monitoring thread
    void stop() {
        if (!running) return;
        
        running = false;
        if (sensor_thread.joinable()) {
            sensor_thread.join();
        }
    }
    
    // Check if a flame was detected in the last MAX_READINGS readings
    bool was_flame_detected() const {
        std::lock_guard<std::mutex> lock(readings_mutex);
        
        for (const auto& reading : readings) {
            if (reading) {
                return true;  // If even one reading detected flame, returns true
            }
        }
        
        return false;  // No flame detected
    }
};

int main() {
    // Flame detector instance
    FlameDetector detector;
    
    // Start sensor monitoring
    detector.start();
    
   // Crow Application Setup
    crow::SimpleApp app;
    
    // API endpoint to check if a flame has been detected
    CROW_ROUTE(app, "/flame_status")
    ([&detector]() {
        crow::json::wvalue response;
        response["flame_detected"] = detector.was_flame_detected();
        return response;
    });
    
    // Server startup
    std::cout << "Server avviato sulla porta 18080..." << std::endl;
    app.port(18083).multithreaded().run();
    
    // Stop the detector when the program ends
    detector.stop();
    
    return 0;
}
