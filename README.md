# IoT-vineyard
IoT monitoring for vineyard

Vineyard monitoring temperature, soil mosture, humidity and luminosity.


## Functional Requirements

| Requirement ID | Functionality Description                                                                                   | Input                         | Output                                     |
|----------------|-------------------------------------------------------------------------------------------------------------|-------------------------------|-------------------------------------------|
| FR1            | The system can monitor the temperature.                                                                     | Temperature reading           | System status update                      |
| FR2            | The system can monitor the humidity.                                                                        | Humidity reading              | System status update                      |
| FR3            | The system can monitor soil moisture.                                                                       | Soil moisture reading         | System status update                      |
| FR4            | The system can monitor the luminance provided to the grapevines.                                            | Luminance reading             | System status update                      |
| FR5            | The system can provide statistics of the mean values of measurements.                                        | Grapevines’ status            | Statistics are provided on request through a Telegram bot. |
| FR6            | The system could warn the user if the values measured by the sensors are different than the desired ones.    | Grapevines’ status            | A notification is sent to the user.       |
| FR7            | The system can provide the user with information about the grapevines through an online interface.           | User requests information     | Information about the grapevines          |
| FR8            | The system is able to identify if a user is allowed to access the system.                                    | User identification           | User allowed                              |
| FR9            | Clusters can evaluate their status by comparing their measurements with neighbors’ clusters.                | Cluster measurements          | Cluster status                            |


-PYTHON SERVER WITH FLASK
-MONGO DB
-ARDUINO AND ESP32 WITH SENSORS
