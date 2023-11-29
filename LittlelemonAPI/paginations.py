from rest_framework.pagination import PageNumberPagination


class MenuItemPagnation(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "pre-page"
    max_page_size = 20
    page_size = 5
