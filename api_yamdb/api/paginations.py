from rest_framework.pagination import PageNumberPagination


class GenreCategoryPagination(PageNumberPagination):
    page_size = 5
