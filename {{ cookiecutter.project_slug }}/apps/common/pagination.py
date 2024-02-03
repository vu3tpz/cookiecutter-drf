from rest_framework.pagination import PageNumberPagination


class AppPagination(PageNumberPagination):
    """
    Pagination class used across the app. Every list view uses
    pagination for better performance.
    """

    page_size = 24
    page_size_query_param = "page-size"
    max_page_size = 100
