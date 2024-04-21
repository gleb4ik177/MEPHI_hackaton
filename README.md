# Tg-bot_for_traffic_predictions+query_recognition
## ТГ бот проекта 
https://t.me/MskSubwayBot
## Описание решения:
В тг бот, описанный в файле tg_bot/Bot.py, пользователь в свободном формате отправляет запрос, содержащий интересующую его станцию и временной период.
Затем, текст пользователя отправляется в LLAMA (в данном случае через LLAMA API), предобученную для задачи function calling, после чего обрабатывается и очищается от возможных ошибок.
По обработанным данным мы выводим статистику пассажиропотока и при необходимости строим предсказания, а если данных больше 10, то пользователю также предоставляется график.
Если случилась ошибка на стороне модели, то пользователю выводится текст, сообщающий об этом.
В файле tg_bot/tg_services.py описана логика обраотки данных и получение предсказания с помощью модели Holt-Winters.

## Researches description
В папке researches описано исследование и построение базовых моделей предсказания временного ряда, а также применение yandexgpt-pro к нашей задаче

