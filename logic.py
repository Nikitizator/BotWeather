#Основная логика для работы бота
import requests
from config import *

def get_weather_info(city, target_hour=None, days=1):
    try:
        #Берем широту и долготу города для сервиса погоды
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        #Превращаем ответ от сервиса и преобразуем в json(словарь), для удобства парсинга
        geo_result = requests.get(geo_url, timeout=10).json()

        if not geo_result.get('results'):
            return "Город не найден. Попробуй уточнить название."

        #Открываем results и ищем в нем index 0
        location = geo_result['results'][0]
        #Открываем переменную location, и ищем по key значения широты и долготы(понадобится для сервиса с погодой), и записывая их value в переменную
        lat, lon = location['latitude'], location['longitude']
        #Открываем переменную location, и ищем по key название города, по умолчанию city
        city_name = location.get('name', city)

        #Обращаемся к API, используя выше полученные данные и получаем нужные нам метрики
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,weather_code,surface_pressure,wind_speed_10m,visibility"
            f"&hourly=temperature_2m,weather_code,surface_pressure,wind_speed_10m,visibility,uv_index"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code,sunrise,sunset,uv_index_max"
            f"&timezone=auto&forecast_days=7"
        )
        #Создаем переменную со значением - ответ от сервера с погодой, и преобразуем в json(словарь)
        web_full_dic = requests.get(weather_url, timeout=10).json()
        #Если день с погодой отсутствует, выводим ошибку
        if 'daily' not in web_full_dic:
            return f"⚠️ Ошибка: Данные для '{city_name}' временно недоступны."

        daily = web_full_dic['daily']
        #Словарь с расшифровкой кода погоды(openmeteo выводит погоду в формате кода, мы преобразуем этот код в читабельный вид с помощью словаря)
        weather_status = {
            0: "Ясно ☀️", 1: "Частично облачно 🌤️", 2: "Умеренно облачно ⛅", 3: "Облачно ☁️",
            45: "Туман 🌫️", 51: "Морось 🌦️", 61: "Дождь 🌧️", 71: "Снег 🌨️", 95: "Гроза ⛈️"
        }
        #Если не заданно кол-во дней, выводим в конкретный час (если target_hour не пустой)
        if days <= 1:
            if target_hour is not None:
                #Находим час и ищем: Температуру, скорость ветра, давление, видимость, уф, статус погоды, и записываем час
                h = web_full_dic['hourly']
                temp = int(h['temperature_2m'][target_hour])
                wind = h['wind_speed_10m'][target_hour]
                pressure = h['surface_pressure'][target_hour]
                vis = h['visibility'][target_hour]
                uv = h['uv_index'][target_hour] # Получаем УФ на час
                status = weather_status.get(h['weather_code'][target_hour], "Непонятно🤐")
                time_label = f" на {target_hour}:00"
            else:
                #Если день задан, находим его и ищем: УФ, темп, Скорость ветра, давление, видимость, статус погоды, время оставляем пустым так как ищем показания на весь день, переводим давление в мм. рт. ст. и видимость в км
                cur = web_full_dic['current']
                # В current API Open-Meteo UV-индекс не всегда есть, берем максимальный за сегодня
                uv = daily['uv_index_max'][0]
                temp = int(cur['temperature_2m'])
                wind = cur['wind_speed_10m']
                pressure = cur['surface_pressure']
                vis = cur['visibility']
                status = weather_status.get(cur['weather_code'], "Непонятно🤐")
                time_label = ""
            mm = int(pressure * 0.750062)
            vis_km = int(vis / 1000)
            #Советы для определенного часа
            report = [
                f"🌍 Погода в городе {city_name}{time_label}: {temp}°C, {status}",
                f"\n🧥 {advice_temp(temp)}",
                f"\n☀️ УФ-индекс: {uv}. {advice_uv(uv)}", # Добавили в отчет
                f"\n💨 Ветер: {wind} км/ч. {advice_wind(wind)}",
                f"\n👁️ Видимость: {vis_km}км {advice_visibility(vis_km)}",
                f"\n🌡️ Сегодня: от {int(daily['temperature_2m_min'][0])}°C до {int(daily['temperature_2m_max'][0])}°C\n{advice_range(int(daily['temperature_2m_max'][0]), int(daily['temperature_2m_min'][0]))}",
                f"\n🌅 Рассвет: {daily['sunrise'][0][-5:]} | Закат: {daily['sunset'][0][-5:]}\n{advice_daylight(daily['sunrise'][0][-5], daily['sunset'][0][-5])}",
                f"\n📍 Давление: {mm} мм рт. ст. {advice_pressure_mm(mm)}"
            ]
            return '\n'.join(report)

        else:
            #Советы для промежутка дней от и до
            full_report = [f"🌍 Прогноз погоды в г. {city_name} на {days} дней.\n"]
            #Цикл от 0 до days
            for i in range(days):
                if i >= len(daily['time']): break
                #Находим макс.темп, мин.темп, средняя, УФ, статус погоды и добавляем к каждой дате свой отсчет
                date = daily['time'][i]
                max_t = int(daily['temperature_2m_max'][i])
                min_t = int(daily['temperature_2m_min'][i])
                avg_t = (max_t + min_t) // 2
                uv_max = daily['uv_index_max'][i]
                status = weather_status.get(daily['weather_code'][i], "Непонятно🤐")

                full_report.append(
                    f"📅 **Дата: {date[8:10]}.{date[5:7]}**\n"
                    f"🌡️ {avg_t}°C, {status}\n"
                    f"☀️ УФ: {uv_max}. {advice_uv(uv_max)}\n"
                    f"🧥 {advice_temp(avg_t)}\n"
                    f"🌡️ От {min_t}° до {max_t}°C\n"
                    f"🌅 {daily['sunrise'][i][-5:]} | 🌇 {daily['sunset'][i][-5:]}\n"
                    f"━━━━━━━━━━━━"
                )
            return '\n'.join(full_report)

    except Exception as e:
        return f"⚠️ Произошла ошибка: {str(e)}"