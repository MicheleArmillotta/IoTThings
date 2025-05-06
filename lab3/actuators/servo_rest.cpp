#include "crow.h"
#include <wiringPi.h>
#include <thread>
#include <chrono>
#include <atomic>
#include <iostream>
#include <signal.h>

constexpr int SERVO_PIN = 17;
constexpr int MIN_PULSE_WIDTH = 500;  // 0.5ms per 0°
constexpr int MAX_PULSE_WIDTH = 2500; // 2.5ms per 180°

std::atomic<bool> fan_active(false);

void move_servo(int pulse_width_us) {
    // Send A pulse of 'pulse_width_us' microseconds
    digitalWrite(SERVO_PIN, HIGH);
    delayMicroseconds(pulse_width_us);
    digitalWrite(SERVO_PIN, LOW);
    // Minimum wait required between commands (3-5ms is usually sufficient)
    delayMicroseconds(5000);
}

void fan_simulation() {
    if (wiringPiSetupGpio() == -1) {
        std::cerr << "Error initializing wiringPi!" << std::endl;
        fan_active = false;
        return;
    }
    
    pinMode(SERVO_PIN, OUTPUT);
    std::cout << "Servo movement at maximum speed" << std::endl;
    
    auto start = std::chrono::steady_clock::now();
    auto duration = std::chrono::seconds(10);
    
    int position = 0;  // 0 = posizione 0°, 1 = posizione 180°
    
    while (std::chrono::steady_clock::now() - start < duration && fan_active) {
        // Direct movement from one extreme to the other at maximum speed
        if (position == 0) {
            std::cout << "Movimento a 180°" << std::endl;
            // Send 10 pulses to the desired position to ensure the servo reaches the position
            for (int i = 0; i < 10 && fan_active; i++) {
                move_servo(MAX_PULSE_WIDTH);
            }
            position = 1;
        } else {
            std::cout << "Movimento a 0°" << std::endl;
            // Send 10 pulses to the desired position to ensure the servo reaches the position
            for (int i = 0; i < 10 && fan_active; i++) {
                move_servo(MIN_PULSE_WIDTH);
            }
            position = 0;
        }
    }
    
    // Stop the servo in neutral position before exiting
    std::cout << "I bring the servo back to the central position..." << std::endl;
    for (int i = 0; i < 5; i++) {
        move_servo(1500);
    }
    
    std::cout << "Fan simulation completed." << std::endl;
    fan_active = false;
}

int main() {
    crow::SimpleApp app;
    
    CROW_ROUTE(app, "/activate_fan").methods("POST"_method)
    ([](const crow::request& req) {
        if (fan_active) {
            return crow::response(409, "Fan already active");
        }
        fan_active = true;
        std::thread(fan_simulation).detach();
        return crow::response(200, "Fan on for 10 seconds");
    });
    
    // We also add an endpoint to stop the fan if needed
    CROW_ROUTE(app, "/stop_fan").methods("POST"_method)
    ([](const crow::request& req) {
        if (!fan_active) {
            return crow::response(404, "Ventilatore non attivo");
        }
        fan_active = false;
        return crow::response(200, "Interruzione del ventilatore richiesta");
    });
    
    app.port(18081).multithreaded().run();
    return 0;
}
