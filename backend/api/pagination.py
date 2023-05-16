from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Класс Пагинации."""

    page_size_query_param = 'limit'
    page_size = 6