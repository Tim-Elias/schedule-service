import logging

# Логгер для отслеживания событий приложения
app_logger = logging.getLogger('app_logger')
app_logger.setLevel(logging.DEBUG)

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Формат логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
app_logger.addHandler(console_handler)

# Пример использования в коде
app_logger.debug("Это отладочное сообщение")
app_logger.info("Это информационное сообщение")
app_logger.error("Это сообщение об ошибке")
