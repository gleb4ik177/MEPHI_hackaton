# Tg-bot_for_traffic_predictions+query_recognition
## ТГ бот проекта 
https://t.me/MskSubwayBot
## Презентация проекта
https://onedrive.live.com/edit?id=9BEF8A041A68B6E9!sb791a3addc3b43698c46b102ada8f45b&resid=9BEF8A041A68B6E9!sb791a3addc3b43698c46b102ada8f45b&cid=9bef8a041a68b6e9&ithint=file%2Cpptx&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3AvYy85YmVmOGEwNDFhNjhiNmU5L0VhMmprYmM3M0dsRGpFYXhBcTJvOUZzQkZDRktxaElEVWVXTlIyZnlPTmRtd0E_ZT03MWJSTFk&migratedtospo=true&wdo=2
## Описание решения:
В тг бот, описанный в файле tg_bot/Bot.py, пользователь в свободном формате отправляет запрос, содержащий интересующую его станцию и временной период.
Затем, текст пользователя отправляется в LLAMA (в данном случае через LLAMA API), предобученную для задачи function calling, после чего обрабатывается и очищается от возможных ошибок.
По обработанным данным мы выводим статистику пассажиропотока и при необходимости строим предсказания, а если данных больше 10, то пользователю также предоставляется график.
Если случилась ошибка на стороне модели, то пользователю выводится текст, сообщающий об этом.
В файле tg_bot/tg_services.py описана логика обраотки данных и получение предсказания с помощью модели Holt-Winters.

## Researches description
В папке researches описано исследование и построение базовых моделей предсказания временного ряда, а также применение yandexgpt-pro к нашей задаче

