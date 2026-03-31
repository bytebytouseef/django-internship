from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination,
    CursorPagination
)
from rest_framework.response import Response


class StandardPageNumberPagination(PageNumberPagination):
    """
    PageNumberPagination — classic ?page=2&page_size=20 style.

    URL: GET /api/v1/products/?page=2&page_size=5
    Response includes: count, next, previous, results

    This is the global default (set in REST_FRAMEWORK settings).
    """
    page_size = 10                      # Default items per page
    page_size_query_param = 'page_size' # Client can override: ?page_size=20
    max_page_size = 100                 # Never return more than 100 items
    page_query_param = 'page'           # ?page=3

    def get_paginated_response(self, data):
        """Override to add extra metadata to pagination response."""
        return Response({
            'success': True,
            'pagination': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'results': data,
        })


class LargeResultsSetPagination(LimitOffsetPagination):
    """
    LimitOffsetPagination — database-style ?limit=10&offset=20.
    More flexible than page numbers. Good for infinite scroll.

    URL: GET /api/v1/products/?limit=10&offset=20
    """
    default_limit = 20
    max_limit = 200
    limit_query_param = 'limit'
    offset_query_param = 'offset'


class SmallResultsSetPagination(PageNumberPagination):
    """Small page size for related/nested resources."""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 25


class OrderCursorPagination(CursorPagination):
    """
    CursorPagination — most scalable, uses a cursor instead of page numbers.
    Great for large datasets and real-time feeds.
    Guarantees no duplicate/missing items even if data changes between pages.

    URL: GET /api/v1/orders/?cursor=<opaque_cursor_string>
    """
    page_size = 10
    ordering = '-created_at'    # Must specify ordering field
    cursor_query_param = 'cursor'