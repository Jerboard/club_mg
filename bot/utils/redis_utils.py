from init import redis_client


# записываем начало старта рекурента
def set_start_recurrent():
    redis_client.setex("start_recurrent", 43200, "1")
    print("✅ Ключ 'start_recurrent' установлен на 12 часов!")


# проверяем запускался ли реккурент последние 12 часов
def is_start_recurrent_set():
    return redis_client.exists("start_recurrent") == 1  # True, если ключ есть
