import asyncio
import datetime
import logging
import os
import random

import aioserial

logger = logging.getLogger(__name__)

GENERATE_FAKE_VALUES = bool(int(os.getenv("GENERATE_FAKE_VALUES", False)))


async def read_sensor_data() -> dict:
    try:
        serial_port = aioserial.AioSerial("/dev/ttyAMA0", 115200)
        received_data = (await serial_port.readline_async()).decode('utf-8')
        parsed_data = decode_received_data(received_data)

        current_time = datetime.datetime.now()
        formatted_data = {
            "id": 1,  # это всё где-то хранить надо и доставать откуда-то, но мне такого таска не давали сори
            "type": 1,
            "number": 1,
            "status": 1,
            "charge": 1,
            "temperature_MK": 1,
            "data": {
                "second": current_time.second,
                "minute": current_time.minute,
                "hour": current_time.hour,
                "day": current_time.day,
                "month": current_time.month,
                "year": current_time.year
            },
            "controlerleack": {  # todo: rename to leak, sc: https://t.me/c/1508598838/1439
                "leack": 0
            },
            "controlermodule": {
                "temperature": parsed_data.get("temperature", None),
                "humidity": parsed_data.get("humidity", None),
                "pressure": parsed_data.get("pressure", None),
                "gas": parsed_data.get("gas", None)
            },
            "controlerenviroment": {
                "temperature": parsed_data.get("temperature", None),
                "humidity": parsed_data.get("humidity", None),
                "pressure": parsed_data.get("pressure", None),
                "VOC": parsed_data.get("VOC", None),
                "gas1": parsed_data.get("gas1", None),
                "gas2": parsed_data.get("gas2", None),
                "gas3": parsed_data.get("gas3", None),
                "pm1": parsed_data.get("pm1", None),
                "pm25": parsed_data.get("pm25", None),
                "pm10": parsed_data.get("pm10", None),
                "fire": parsed_data.get("fire", None),
                "smoke": parsed_data.get("smoke", None)
            }
        }

        return formatted_data

    except Exception as e:
        print(f"Error reading sensor data: {e}")
        return {}


def decode_received_data(received_data: str) -> dict:
    data = received_data.split()
    decoded_data = {}

    try:
        # Первые два байта - тип и номер
        decoded_data["type"] = int(data[0], 16)
        decoded_data["number"] = int(data[1], 16)

        # В зависимости от типа и номера определяем формат и расшифровываем данные
        if decoded_data["type"] == 0x0000:  # Резерв
            pass  # Данные не обрабатываются
        elif decoded_data["type"] == 0x0001:  # ГК
            decoded_data["charge"] = int(data[2])
        elif decoded_data["type"] == 0x0002:  # Модульный датчик (резерв)
            decoded_data["temperature_MK"] = int(data[3], 16)
        elif decoded_data["type"] == 0x0010:  # Датчик протечки
            decoded_data["leak"] = int(data[5])
        elif decoded_data["type"] == 0x0011:  # Модульный датчик
            decoded_data["leak"] = int(data[5])
        elif decoded_data["type"] == 0x0012:  # Датчик окружающей среды
            if decoded_data["number"] == 1:  # Модульный датчик
                decoded_data["temperature"] = int(data[5], 16)
                decoded_data["humidity"] = int(data[9], 16)
                decoded_data["pressure"] = int(data[13], 16)
                decoded_data["gas"] = int(data[17], 16)
            elif decoded_data["number"] == 2:  # Датчик окружающей среды
                decoded_data["temperature"] = int(data[5], 16)
                decoded_data["humidity"] = int(data[9], 16)
                decoded_data["pressure"] = int(data[13], 16)
                decoded_data["VOC"] = int(data[17], 16)
                decoded_data["gas1"] = int(data[21], 16)
                decoded_data["gas2"] = int(data[25], 16)
                decoded_data["gas3"] = int(data[29], 16)
                decoded_data["pm1"] = int(data[33], 16)
                decoded_data["pm25"] = int(data[35], 16)
                decoded_data["pm10"] = int(data[37], 16)
                decoded_data["fire"] = int(data[39], 16)
                decoded_data["smoke"] = int(data[41], 16)
    except IndexError:
        logger.error("Error decoding data: not enough data")
        return {}
    except ValueError:
        logger.error("Error decoding data: invalid format")
        return {}

    return decoded_data


if GENERATE_FAKE_VALUES:
    # generate list of 10 fake ids
    fake_ids = random.sample(range(1, 100), 10)
    sensor_types_values = {
        "gk": ["charge", ],
        "module": ["temperature_MK", ],
        "leak": ["leak", ],
        "module_env": ["temperature", "humidity", "pressure", "gas", ],
        "env": ["temperature", "humidity", "pressure", "VOC", "gas1", "gas2", "gas3", "pm1", "pm25", "pm10", "fire",
                "smoke", ]
    }


    async def read_sensor_data() -> dict:
        await asyncio.sleep(random.randint(1, 10))
        sensor_type = random.choice(list(sensor_types_values.keys()))
        sensor_type_values = sensor_types_values[sensor_type]
        current_time = datetime.datetime.now()

        parsed_data = {}
        for value in sensor_type_values:
            parsed_data[value] = random.randint(0, 100)

        fake_data = {
            "id": random.choice(fake_ids),
            "type": 0,
            "number": 1,
            "status": 1,
            "charge": parsed_data.get("charge", None),
            "temperature_MK": parsed_data.get("temperature_MK", None),
            "data": {
                "second": current_time.second,
                "minute": current_time.minute,
                "hour": current_time.hour,
                "day": current_time.day,
                "month": current_time.month,
                "year": current_time.year
            },
        }

        if sensor_type == "gk":
            fake_data += {
                "controlergk": {
                    "charge": parsed_data.get("charge", None)
                }
            }

        if sensor_type == "module":
            fake_data += {
                "temperature_MK": parsed_data.get("temperature_MK", None)
            },

        if sensor_type == "leak":
            fake_data += {
                "controlerleak": {
                    "leak": parsed_data.get("leak", None)
                },
            }
        if sensor_type == "module_env":
            fake_data += {
                "controlermodule": {
                    "temperature": parsed_data.get("temperature", None),
                    "humidity": parsed_data.get("humidity", None),
                    "pressure": parsed_data.get("pressure", None),
                    "gas": parsed_data.get("gas", None)
                },
            }
        if sensor_type == "env":
            fake_data += {
                "controlerenviroment": {
                    "temperature": parsed_data.get("temperature", None),
                    "humidity": parsed_data.get("humidity", None),
                    "pressure": parsed_data.get("pressure", None),
                    "VOC": parsed_data.get("VOC", None),
                    "gas1": parsed_data.get("gas1", None),
                    "gas2": parsed_data.get("gas2", None),
                    "gas3": parsed_data.get("gas3", None),
                    "pm1": parsed_data.get("pm1", None),
                    "pm25": parsed_data.get("pm25", None),
                    "pm10": parsed_data.get("pm10", None),
                    "fire": parsed_data.get("fire", None),
                    "smoke": parsed_data.get("smoke", None)
                }
            }

        return fake_data
