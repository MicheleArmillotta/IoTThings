#include "crow.h" // Assicurati di avere crow_all.h
#include <gpiod.h>
#include <thread>
#include <chrono>
#include <atomic>

constexpr char* CHIPNAME = "gpiochip0";  // Tipico su Raspberry Pi OS
constexpr int GPIO_PIN = 19;             // GPIO 19 (Pin fisico 35)

std::atomic<bool> buzzer_active(false);

// Funzione per far suonare il buzzer
void buzzer_alarm() {
    gpiod_chip* chip = gpiod_chip_open_by_name(CHIPNAME);
    if (!chip) {
        std::cerr << "Failed to open GPIO chip\n";
        return;
    }

    gpiod_line* line = gpiod_chip_get_line(chip, GPIO_PIN);
    if (!line) {
        std::cerr << "Failed to get GPIO line\n";
        gpiod_chip_close(chip);
        return;
    }

    if (gpiod_line_request_output(line, "buzzer", 0) < 0) {
        std::cerr << "Failed to set GPIO line as output\n";
        gpiod_chip_close(chip);
        return;
    }

    auto start = std::chrono::steady_clock::now();
    auto duration = std::chrono::seconds(10);

    // Cicla per 10 secondi
    while (std::chrono::steady_clock::now() - start < duration) {
        gpiod_line_set_value(line, 1);
        std::this_thread::sleep_for(std::chrono::microseconds(500));  // mezzo millisecondo acceso

        gpiod_line_set_value(line, 0);
        std::this_thread::sleep_for(std::chrono::microseconds(500));  // mezzo millisecondo spento
    }

    // Spegni il buzzer
    gpiod_line_set_value(line, 0);

    gpiod_line_release(line);
    gpiod_chip_close(chip);

    buzzer_active = false;
}

int main() {
    crow::SimpleApp app;

    CROW_ROUTE(app, "/activate_buzzer").methods("POST"_method)
    ([](const crow::request& req) {
        if (buzzer_active) {
            return crow::response(409, "Buzzer already active");
        }

        buzzer_active = true;
        std::thread(buzzer_alarm).detach(); // Lancia in thread separato
        return crow::response(200, "Buzzer activated for 10 seconds");
    });

    app.port(18080).multithreaded().run();
}
