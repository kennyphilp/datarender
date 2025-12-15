from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.db.models import QuerySet
import os
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import SchoolRoll
from .constants import (
    YEARS,
    GRAPH_COLOR_PALETTE,
    GRAPH_STYLE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MAX_SCHOOLS_PER_GRAPH,
)
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'home/index.html')

def data_api(request: HttpRequest) -> JsonResponse:
    """
    Paginated API for school roll data.
    
    Query params:
      - page: 1-based page number (default: 1)
      - page_size: items per page (default: DEFAULT_PAGE_SIZE, max: MAX_PAGE_SIZE)
      - sort: column name to sort by (default: 'Name')
      - order: 'asc' or 'desc' (default: 'asc')
      - sector: optional filter by Sector
      - schools: repeated param to filter by Name
      
    Returns:
        JsonResponse: Paginated data with metadata
    """
    qs = SchoolRoll.objects.using('datastore').all()

    # Filtering
    sector = request.GET.get('sector')
    if sector:
        qs = qs.filter(Sector=sector)

    selected_schools = request.GET.getlist('schools')
    if selected_schools:
        qs = qs.filter(Name__in=selected_schools)

    # Sorting
    sort = request.GET.get('sort', 'Name')
    order = request.GET.get('order', 'asc')
    if sort:
        # Prevent SQL injection by allowing only known column names
        allowed = {f.name for f in SchoolRoll._meta.fields}
        if sort in allowed:
            prefix = '' if order == 'asc' else '-'
            qs = qs.order_by(f"{prefix}{sort}")

    # Pagination with validation
    try:
        page = int(request.GET.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid page parameter: {e}")
        page = 1
    
    try:
        page_size = int(request.GET.get('page_size', DEFAULT_PAGE_SIZE))
        page_size = max(1, min(page_size, MAX_PAGE_SIZE))  # Clamp between 1 and MAX
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid page_size parameter: {e}")
        page_size = DEFAULT_PAGE_SIZE

    paginator = Paginator(qs, page_size)
    try:
        page_obj = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.page(1)

    # Build columns list (use DB column names)
    columns = [f.name for f in SchoolRoll._meta.fields]

    # Convert objects to dicts
    data = [obj.to_dict() for obj in page_obj.object_list]

    # Distinct values for filters (whole table)
    distinct_names_qs = SchoolRoll.objects.using('datastore').order_by('Name').values_list('ObjectId', 'Name').distinct()
    distinct_sectors_qs = SchoolRoll.objects.using('datastore').order_by('Sector').values_list('Sector', flat=True).distinct()
    distinct_types_qs = SchoolRoll.objects.using('datastore').order_by('School_Type').values_list('School_Type', flat=True).distinct()

    distinct = {
        'names': [{'id': oid, 'name': name} for oid, name in distinct_names_qs if name],
        'sectors': [s for s in distinct_sectors_qs if s],
        'types': [t for t in distinct_types_qs if t],
    }

    return JsonResponse({
        'page': page_obj.number,
        'page_size': page_size,
        'total': paginator.count,
        'total_pages': paginator.num_pages,
        'columns': columns,
        'data': data,
        'distinct': distinct,
    })

def enrollment_graph(request: HttpRequest) -> HttpResponse:
    """
    Generate enrollment trend graph for selected schools.
    
    Query params:
      - ids: Repeated ObjectId values for schools to plot
      - schools: Repeated school names (fallback if ids not provided)
      
    Returns:
        HttpResponse: PNG image of enrollment trends
    """
    # Get selected identifiers: support repeated `ids` (ObjectId) or repeated `schools` (Name)
    selected_ids = request.GET.getlist('ids') or []
    selected_schools = []
    if not selected_ids:
        selected_schools = request.GET.getlist('schools') or []

    # Create appropriate graph based on selection
    if not selected_ids and not selected_schools:
        fig = _create_empty_graph()
    else:
        queryset = _fetch_enrollment_data(selected_ids, selected_schools)
        fig = _plot_enrollment_data(queryset)
    
    # Save plot to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    response['Cache-Control'] = 'no-cache'
    return response

def _fetch_enrollment_data(selected_ids: Optional[List[str]] = None, selected_schools: Optional[List[str]] = None) -> QuerySet[SchoolRoll]:
    """
    Fetch enrollment data for specified schools.
    
    Args:
        selected_ids: List of ObjectId values
        selected_schools: List of school names
        
    Returns:
        QuerySet of SchoolRoll objects
    """
    if selected_ids:
        # Limit to prevent excessive graph complexity
        limited_ids = selected_ids[:MAX_SCHOOLS_PER_GRAPH]
        if len(selected_ids) > MAX_SCHOOLS_PER_GRAPH:
            logger.warning(f"Requested {len(selected_ids)} schools, limited to {MAX_SCHOOLS_PER_GRAPH}")
        return SchoolRoll.objects.using('datastore').filter(ObjectId__in=limited_ids)
    elif selected_schools:
        limited_schools = selected_schools[:MAX_SCHOOLS_PER_GRAPH]
        if len(selected_schools) > MAX_SCHOOLS_PER_GRAPH:
            logger.warning(f"Requested {len(selected_schools)} schools, limited to {MAX_SCHOOLS_PER_GRAPH}")
        return SchoolRoll.objects.using('datastore').filter(Name__in=limited_schools)
    return SchoolRoll.objects.using('datastore').none()


def _create_empty_graph() -> Figure:
    """
    Create a placeholder graph when no schools are selected.
    
    Returns:
        matplotlib Figure object
    """
    with plt.rc_context(GRAPH_STYLE):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Select schools to view enrollment trends',
                ha='center', va='center', transform=ax.transAxes, fontsize=14)
        ax.set_xlim(YEARS[0], YEARS[-1])
        ax.set_ylim(0, 1000)
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Pupils')
        ax.set_title('School Enrollment Trends')
        ax.grid(True, alpha=0.3, color=GRAPH_STYLE['grid.color'])
    return fig


def _plot_enrollment_data(queryset: QuerySet[SchoolRoll]) -> Figure:
    """
    Create enrollment trend plot from queryset data.
    
    Args:
        queryset: QuerySet of SchoolRoll objects
        
    Returns:
        matplotlib Figure object
    """
    year_columns = [f'F{year}' for year in YEARS]
    
    with plt.rc_context(GRAPH_STYLE):
        fig, ax = plt.subplots(figsize=(12, 6))
        
        plotted_count = 0
        for obj in queryset:
            enrollment_data = [getattr(obj, col) for col in year_columns]
            
            # Filter out None/null values
            valid_data = [
                (year, enrollment) 
                for year, enrollment in zip(YEARS, enrollment_data) 
                if enrollment is not None
            ]
            
            if valid_data:
                plot_years, plot_enrollment = zip(*valid_data)
                color = GRAPH_COLOR_PALETTE[plotted_count % len(GRAPH_COLOR_PALETTE)]
                ax.plot(
                    plot_years, plot_enrollment, 
                    marker='o', linewidth=2, markersize=4, 
                    label=obj.Name, color=color
                )
                plotted_count += 1
        
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Pupils')
        ax.set_title(
            f'Enrollment Trends for {plotted_count} Selected School'
            f'{"s" if plotted_count != 1 else ""}'
        )
        ax.grid(True, alpha=0.3, color=GRAPH_STYLE['grid.color'])
        
        if plotted_count > 0:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
        
        fig.tight_layout()
    
    return fig


def data_page(request: HttpRequest) -> HttpResponse:
    """Render the main data exploration page."""
    return render(request, 'home/data.html')
