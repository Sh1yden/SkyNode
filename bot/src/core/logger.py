import logging


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Получить логгер для модуля.

    Args:
        name: Имя логгера. Если None, используется имя вызывающего модуля.

    Returns:
        Logger: Настроенный логгер
    """
    if name is None:
        # Автоматическое определение имени модуля (медленно, не рекомендуется)
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back:
            name = frame.f_back.f_globals.get("__name__", "unknown")

    # Все логгеры должны быть дочерними от telegram_bot
    if not name.startswith("telegram_bot."):
        name = f"telegram_bot.{name}"

    return logging.getLogger(name)


class LoggerMixin:
    """
    Миксин для добавления логгера в классы.

    Пример:
        class MyService(LoggerMixin):
            def process(self):
                self.logger.info("Processing...")
    """

    @property
    def logger(self) -> logging.Logger:
        """Логгер с именем класса"""
        if not hasattr(self, "_logger"):
            class_name = self.__class__.__name__
            module_name = self.__class__.__module__
            self._logger = get_logger(f"{module_name}.{class_name}")
        return self._logger
