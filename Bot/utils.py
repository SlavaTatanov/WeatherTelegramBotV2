def req_counter(key):
    """
    Счетчик запросов к API
    Если функция до этого закеширована то счетчик не меняется,
    так как нет запуска функции
    """
    req_counter.storage = {}

    def req_counter_dec(fun):
        async def wrapper(*args, **kwargs):
            counter = req_counter.storage.get(key, 0)
            counter += 1
            req_counter.storage[key] = counter
            return await fun(*args, **kwargs)
        return wrapper
    return req_counter_dec
