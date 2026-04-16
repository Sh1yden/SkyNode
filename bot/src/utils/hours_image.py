import asyncio
import io
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Any


async def generate_hourly_forecast_image(
    weather_data: Dict[str, List[Dict[str, Any]]], hours_count: int = 24
) -> io.BytesIO:
    return await asyncio.to_thread(_draw_forecast_table, weather_data, hours_count)


def _draw_forecast_table(
    weather_data: Dict[str, List[Dict[str, Any]]], hours_count: int
) -> io.BytesIO:
    # --- Стили SkyNode (Black & Gold Glass) ---
    COLOR_BG = (10, 10, 10)  # Матовый черный (фон лого)
    COLOR_PANEL = (28, 28, 35)  # Темное стекло
    COLOR_TEXT_TEMP = (210, 190, 150)  # Температура (как нити)
    COLOR_TEXT_DIM = (160, 155, 140)  # Приглушенный беж (как нити)
    COLOR_ACCENT_GOLD = (230, 190, 110)  # Теплое золото (ноды)
    COLOR_ACCENT_BLUE = (120, 160, 240)  # Небесно-голубой (акцент SkyNode)
    COLOR_GRID = (45, 45, 55)  # Границы ячеек

    # --- Геометрия ---
    cell_w, cell_h = 130, 100
    srv_col_w = 200
    margin = 40

    # Берем эталонный список часов из первого сервиса, чтобы сохранить порядок
    first_srv_name = next(iter(weather_data))
    reference_hours = weather_data[first_srv_name][:hours_count]

    if not reference_hours:
        return io.BytesIO()

    img_w = srv_col_w + (len(reference_hours) * cell_w) + (margin * 2)
    img_h = (len(weather_data) + 1) * cell_h + (margin * 2)

    img = Image.new("RGB", (img_w, img_h), color=COLOR_BG)
    draw = ImageDraw.Draw(img)

    try:
        font_path = "assets/fonts/JetBrains Fonts/fonts/ttf/JetBrainsMono-Bold.ttf"
        f_h = ImageFont.truetype(font_path, 24)
        f_m = ImageFont.truetype(font_path, 22)
        f_s = ImageFont.truetype(font_path, 16)
    except OSError:
        f_h = f_m = f_s = ImageFont.load_default()

    # --- Отрисовка ---

    # Подложка таблицы (Матовое стекло)
    draw.rectangle(
        [margin, margin, img_w - margin, img_h - margin],
        fill=COLOR_PANEL,
        outline=COLOR_GRID,
        width=1,
    )

    # Вертикальные колонки времени (Золотые акценты)
    for i, item in enumerate(reference_hours):
        x = margin + srv_col_w + (i * cell_w)
        display_time = item["time"]

        # Рисуем время
        draw.text((x + 30, margin + 35), display_time, fill=COLOR_ACCENT_GOLD, font=f_h)
        # Вертикальная линия сетки
        draw.line([(x, margin), (x, img_h - margin)], fill=COLOR_GRID, width=1)

    # Строки сервисов
    for row_idx, (srv_name, hours_list) in enumerate(weather_data.items()):
        y = margin + (row_idx + 1) * cell_h

        # Горизонтальная линия сетки
        draw.line([(margin, y), (img_w - margin, y)], fill=COLOR_GRID, width=1)

        # Название сервиса (в стиле SkyNode Blue)
        draw.text(
            (margin + 20, y + 35), srv_name.upper(), fill=COLOR_ACCENT_BLUE, font=f_m
        )

        # Рисуем данные сервиса строго по индексу
        for i in range(len(reference_hours)):
            if i >= len(hours_list):
                continue

            x = margin + srv_col_w + (i * cell_w)
            d = hours_list[i]

            temp = d.get("temp", 0)

            temp_str = f"{temp}{d.get('temp_unit', '°')}"
            fl_str = f"fl: {d.get('feels_like', '--')}°"

            # Отрисовка температуры
            draw.text((x + 30, y + 20), temp_str, fill=COLOR_TEXT_TEMP, font=f_m)
            # Отрисовка "ощущается как"
            draw.text((x + 30, y + 55), fl_str, fill=COLOR_TEXT_DIM, font=f_s)

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output


if __name__ == "__main__":
    import os

    async def main_test():
        # Имитируем данные из твоего лога (с повторами времени и переходом через 00:00)
        mock_data = {
            "Yandex": [
                {"time": "22:00", "temp": 8, "temp_unit": "°", "feels_like": 6},
                {"time": "23:00", "temp": 7, "temp_unit": "°", "feels_like": 5},
                {"time": "00:00", "temp": 7, "temp_unit": "°", "feels_like": 5},
                {"time": "01:00", "temp": 6, "temp_unit": "°", "feels_like": 4},
                {"time": "02:00", "temp": 6, "temp_unit": "°", "feels_like": 4},
                # ... имитация завтрашнего вечера, чтобы проверить "разнобой"
                {"time": "22:00", "temp": 10, "temp_unit": "°", "feels_like": 7},
                {"time": "23:00", "temp": 10, "temp_unit": "°", "feels_like": 7},
            ],
            "OpenMeteo": [
                {"time": "22:00", "temp": 9, "temp_unit": "°", "feels_like": 7},
                {"time": "23:00", "temp": 8, "temp_unit": "°", "feels_like": 6},
                {"time": "00:00", "temp": 7, "temp_unit": "°", "feels_like": 5},
                {"time": "01:00", "temp": 5, "temp_unit": "°", "feels_like": 3},
                {"time": "02:00", "temp": 5, "temp_unit": "°", "feels_like": 3},
                {"time": "22:00", "temp": 11, "temp_unit": "°", "feels_like": 8},
                {"time": "23:00", "temp": 11, "temp_unit": "°", "feels_like": 8},
            ],
        }

        print("🌌 SkyNode: Запуск локальной генерации темы...")

        # Вызываем твою функцию
        # Убедись, что hours_count соответствует количеству элементов в mock_data
        image_data = await generate_hourly_forecast_image(mock_data, hours_count=7)

        # Сохраняем результат в файл
        file_name = "skynode_style_test.png"
        with open(file_name, "wb") as f:
            f.write(image_data.getbuffer())

        print(f"✅ Готово! Картинка сохранена: {os.path.abspath(file_name)}")

    # Запуск асинхронного теста
    asyncio.run(main_test())
