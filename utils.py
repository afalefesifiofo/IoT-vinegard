





#FUNZIONI AGGIUNTE


#CERCA ANCHE UN VALORE MASSIMO X LA LUMIONSITA'------------------------------------------------------------
def hour_with_light():
    if global_light_intensity is not None and global_light_intensity > 500: #da controlare per il nostro sensore
        return "ok"
    else:
        return "luminosità non sufficiente"

# Funzione per etichettare la temperatura INSETTO
def risk_lobesia(temp):
    if temp > 35 or temp < 10:
        return "LOW"
    elif 25 <= temp <= 30:
        return "HIGH"
    elif 30 < temp <= 35:
        return "MEDIUM"
    elif 10 <= temp < 25:
        return "MEDIUM"
    else:
        return "Invalid"


def check_soil_moisture(soil_moisture):
    if soil_moisture is not None:
        if 25 <= soil_moisture <= 55:
            return f"The soil moisture is {soil_moisture}%, quality GOOD"
        else:
            return f"The soil moisture is {soil_moisture}%, quality BAD"
    else:
        return "Soil moisture value is None. Sensor has some problems"

# Funzione per verificare l'umidità dell'aria
def check_air_humidity(humidity):
    if humidity is not None:
        if 30 <= humidity <= 80:
            return f"The humidity of the air is {humidity}%, status: GOOD"
        else:
            return f"The humidity of the air is {humidity}%, status: BAD"
    else:
        return "Air humidity value is None. Sensor has some problems"

