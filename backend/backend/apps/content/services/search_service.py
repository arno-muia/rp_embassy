"""PostgreSQL Full Text Search service layer.

Implements PostgreSQL FTS for Django-owned CMS models only.
Per B1_MODEL_OWNERSHIP_MATRIX, Prisma-owned models remain separate.

Architecture:
- SearchVector for field indexing
- SearchQuery for query parsing
- SearchRank for relevance ordering
- GIN indexes via Django migrations
"""

from typing import List, Optional, Tuple, Type

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db import models
from django.db.models import QuerySet


# =============================================================================
# SEARCH VECTOR HELPERS
# =============================================================================

def build_search_vector(
    fields: List[Tuple[str, str]],
) -> SearchVector:
    """Build a SearchVector from field specifications.

    Args:
        fields: List of (field_name, weight) tuples.
                Weight: 'A' (title/names), 'B' (summaries), 'C' (body)

    Returns:
        SearchVector object for queryset annotation.

    Example:
        build_search_vector([
            ('title', 'A'),
            ('content', 'C'),
        ])
    """
    vector = SearchVector(*[f[0] for f in fields])
    return vector


def build_weighted_search_vector(
    fields: List[Tuple[str, str]],
) -> SearchVector:
    """Build a weighted SearchVector.

    Args:
        fields: List of (field_name, weight) tuples.

    Returns:
        SearchVector with weight configuration.
    """
    config = {f[0]: f[1] for f in fields}
    return SearchVector(**config)


def build_search_query(query_string: str, search_type: str = 'plain') -> SearchQuery:
    """Build a SearchQuery for the given query string.

    Args:
        query_string: User search input
        search_type: 'plain', 'phrase', or 'raw'

    Returns:
        SearchQuery object
    """
    return SearchQuery(query_string, search_type=search_type)


# =============================================================================
# SEARCH EXECUTION
# =============================================================================

def execute_search(
    queryset: QuerySet,
    search_vector: SearchVector,
    search_query: SearchQuery,
    rank_field: str = 'rank',
) -> QuerySet:
    """Execute search with ranking on a queryset.

    Args:
        queryset: Base queryset to search
        search_vector: SearchVector defining searchable fields
        search_query: SearchQuery with user input
        rank_field: Name of the rank annotation field

    Returns:
        QuerySet annotated with rank, filtered by query, ordered by rank.
    """
    return queryset.annotate(
        rank=SearchRank(search_vector, search_query),
    ).filter(rank__gt=0).order_by('-rank')


def paginate_results(
    queryset: QuerySet,
    page: int = 1,
    page_size: int = 12,
) -> QuerySet:
    """Paginate queryset results.

    Args:
        queryset: Queryset to paginate
        page: Page number (1-indexed)
        page_size: Number of results per page

    Returns:
        Paginated queryset slice.
    """
    start = (page - 1) * page_size
    end = start + page_size
    return queryset[start:end]


# =============================================================================
# MODEL-SPECIFIC SEARCH
# =============================================================================

# Search field configurations per model
CONTENT_BLOCK_SEARCH = [
    ('title', 'A'),
    ('content', 'C'),
]

ANNOUNCEMENT_SEARCH = [
    ('title', 'A'),
    ('body', 'C'),
]

CHURCH_PROFILE_SEARCH = [
    ('mission', 'C'),
    ('vision', 'C'),
    ('welcome_message', 'C'),
    ('pastor_message', 'C'),
    ('about_text', 'C'),
]

PRAYER_REQUEST_SEARCH = [
    ('title', 'A'),
    ('content', 'C'),
]


def search_content_blocks(query: str, page: int = 1, page_size: int = 12) -> Tuple[QuerySet, float]:
    """Search ContentBlock models.

    Args:
        query: Search query string
        page: Page number
        page_size: Results per page

    Returns:
        Tuple of (paginated queryset, total count)
    """
    from backend.apps.content.models import ContentBlock

    if not query:
        return ContentBlock.objects.none(), 0

    vector = build_weighted_search_vector(CONTENT_BLOCK_SEARCH)
    search_query = build_search_query(query)

    queryset = execute_search(
        ContentBlock.objects.filter(is_active=True), vector, search_query
    )

    # Get count before pagination
    count = queryset.count()

    return paginate_results(queryset, page, page_size), float(count)


def search_announcements(
    query: str, page: int = 1, page_size: int = 12
) -> Tuple[QuerySet, float]:
    """Search Announcement models.

    Args:
        query: Search query string
        page: Page number
        page_size: Results per page

    Returns:
        Tuple of (paginated queryset, total count)
    """
    from backend.apps.events.models import Announcement

    if not query:
        return Announcement.objects.none(), 0

    vector = build_weighted_search_vector(ANNOUNCEMENT_SEARCH)
    search_query = build_search_query(query)

    queryset = execute_search(
        Announcement.objects.filter(is_active=True), vector, search_query
    )

    count = queryset.count()

    return paginate_results(queryset, page, page_size), float(count)


def search_church_profile(
    query: str, page: int = 1, page_size: int = 12
) -> Tuple[QuerySet, float]:
    """Search ChurchProfile models.

    ChurchProfile is typically a singleton, but search is available
    for future multi-campus expansion.

    Args:
        query: Search query string
        page: Page number
        page_size: Results per page

    Returns:
        Tuple of (paginated queryset, total count)
    """
    from backend.apps.content.models import ChurchProfile

    if not query:
        return ChurchProfile.objects.none(), 0

    vector = build_weighted_search_vector(CHURCH_PROFILE_SEARCH)
    search_query = build_search_query(query)

    queryset = execute_search(ChurchProfile.objects.all(), vector, search_query)

    count = queryset.count()

    return paginate_results(queryset, page, page_size), float(count)


def search_prayer_requests(
    query: str, page: int = 1, page_size: int = 12
) -> Tuple[QuerySet, float]:
    """Search PrayerRequest models.

    Args:
        query: Search query string
        page: Page number
        page_size: Results per page

    Returns:
        Tuple of (paginated queryset, total count)
    """
    from backend.apps.prayer.models import PrayerRequest

    if not query:
        return PrayerRequest.objects.none(), 0

    vector = build_weighted_search_vector(PRAYER_REQUEST_SEARCH)
    search_query = build_search_query(query)

    queryset = execute_search(
        PrayerRequest.objects.filter(is_public=True), vector, search_query
    )

    count = queryset.count()

    return paginate_results(queryset, page, page_size), float(count)


# =============================================================================
# UNIFIED SEARCH
# =============================================================================

def unified_search(
    query: str,
    page: int = 1,
    page_size: int = 12,
    include_content_blocks: bool = True,
    include_announcements: bool = True,
    include_church_profile: bool = False,
    include_prayer_requests: bool = True,
) -> dict:
    """Execute unified search across all searchable models.

    Args:
        query: Search query string
        page: Page number
        page_size: Results per page
        include_content_blocks: Include ContentBlock results
        include_announcements: Include Announcement results
        include_church_profile: Include ChurchProfile results
        include_prayer_requests: Include PrayerRequest results

    Returns:
        Dictionary with results grouped by model type.
    """
    results = {}

    if include_content_blocks:
        results['content_blocks'], _ = search_content_blocks(query, page, page_size)

    if include_announcements:
        results['announcements'], _ = search_announcements(
            query, page, page_size
        )

    if include_church_profile:
        results['church_profile'], _ = search_church_profile(
            query, page, page_size
        )

    if include_prayer_requests:
        results['prayer_requests'], _ = search_prayer_requests(
            query, page, page_size
        )

    return results