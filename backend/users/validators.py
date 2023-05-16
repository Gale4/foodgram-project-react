from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    """Проверка юзернейма."""

    regex = r'^[\w.@+-]+\z'
