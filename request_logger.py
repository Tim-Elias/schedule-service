import logging
from logging.handlers import RotatingFileHandler

# Логгер для запросов
request_logger = logging.getLogger('request_logger')
request_logger.setLevel(logging.INFO)

# Обработчик для записи в файл
file_handler = RotatingFileHandler('service_logs.log', maxBytes=1000000, backupCount=5)
file_handler.setLevel(logging.INFO)

# Формат логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
request_logger.addHandler(file_handler)

class RequestLogHandler:
    @staticmethod
    def log_request(entity_name, entity_id=None, url=None, user=None, response_status=None, action=None, is_bulk=False):
        """
        Логирует запрос с информацией о сущности, ID, URL, пользователе и статусе ответа.
        """
        log_type = "Bulk" if is_bulk else "Single"
        request_logger.info(f"{log_type} request - "
                            f"Action: {action}, "
                            f"Entity: {entity_name}, "
                            f"ID: {entity_id if entity_id else 'N/A'}, "
                            f"URL: {url}, "
                            f"User: {user}, "
                            f"Response Status: {response_status}")

    @staticmethod
    def get_logs():
        """
        Читает логи из файла и возвращает их в виде списка.
        """
        with open('service_logs.log', 'r') as log_file:
            logs = log_file.readlines()
        return logs
