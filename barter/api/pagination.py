from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNumberPagination(PageNumberPagination):
    page_size_query_param = 'per_page'

    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'per_page': self.page.paginator.per_page,
            'pages': self.page.paginator.num_pages,
            'has_next': self.page.has_next(),
            'data': data
        })
