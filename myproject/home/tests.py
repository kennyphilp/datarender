from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json
from .models import SchoolRoll
from .constants import (
    YEARS,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    MAX_SCHOOLS_PER_GRAPH,
    GRAPH_COLOR_PALETTE,
)


class SchoolRollModelTests(TestCase):
    """Test cases for the SchoolRoll model."""
    
    databases = ['datastore']
    
    def setUp(self):
        """Set up test data."""
        # Note: Since managed=False, we'll mock the database interactions
        pass
    
    def test_to_dict_includes_all_fields(self):
        """Test that to_dict() includes all required fields."""
        school = SchoolRoll(
            ObjectId='1',
            Code='TEST001',
            Name='Test School',
            LA_Code='100',
            LA_Name='Test Authority',
            Sector='Primary',
            School_Type='Local Authority',
            F1996=100,
            F1997=105,
            F2018=150,
        )
        
        result = school.to_dict()
        
        # Check core fields
        self.assertEqual(result['ObjectId'], '1')
        self.assertEqual(result['Name'], 'Test School')
        self.assertEqual(result['Sector'], 'Primary')
        self.assertEqual(result['School_Type'], 'Local Authority')
        
        # Check year fields
        self.assertEqual(result['F1996'], 100)
        self.assertEqual(result['F1997'], 105)
        self.assertEqual(result['F2018'], 150)
        
        # Verify all years are included
        for year in YEARS:
            self.assertIn(f'F{year}', result)
    
    def test_to_dict_handles_null_values(self):
        """Test that to_dict() properly handles null/None values."""
        school = SchoolRoll(
            ObjectId='2',
            Name='School with Nulls',
            Code=None,
            F1996=None,
            F2018=200,
        )
        
        result = school.to_dict()
        
        self.assertIsNone(result['Code'])
        self.assertIsNone(result['F1996'])
        self.assertEqual(result['F2018'], 200)


class DataAPITests(TestCase):
    """Test cases for the data_api endpoint."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('data_api')
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_returns_paginated_results(self, mock_objects):
        """Test that API returns properly paginated data."""
        # Mock the queryset chain
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        # Create mock school objects
        mock_schools = []
        for i in range(5):
            school = MagicMock(spec=SchoolRoll)
            school.to_dict.return_value = {
                'ObjectId': str(i),
                'Name': f'School {i}',
                'Sector': 'Primary',
                'School_Type': 'Local Authority',
                **{f'F{year}': 100 + i for year in YEARS}
            }
            mock_schools.append(school)
        
        # Mock paginator behavior
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = mock_schools[:3]
            mock_page.number = 1
            mock_paginator.return_value.count = 5
            mock_paginator.return_value.num_pages = 2
            mock_paginator.return_value.page.return_value = mock_page
            
            # Mock distinct queries
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = [
                ('1', 'School 1'),
                ('2', 'School 2'),
            ]
            
            response = self.client.get(self.url, {'page': 1, 'page_size': 3})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['page_size'], 3)
        self.assertEqual(data['total'], 5)
        self.assertEqual(data['total_pages'], 2)
        self.assertEqual(len(data['data']), 3)
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_default_page_size(self, mock_objects):
        """Test that API uses DEFAULT_PAGE_SIZE when not specified."""
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = []
            
            response = self.client.get(self.url)
            
            # Verify Paginator was called with DEFAULT_PAGE_SIZE
            mock_paginator.assert_called_once()
            args = mock_paginator.call_args[0]
            self.assertEqual(args[1], DEFAULT_PAGE_SIZE)
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_clamps_page_size_to_max(self, mock_objects):
        """Test that API enforces MAX_PAGE_SIZE limit."""
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = []
            
            # Request more than MAX_PAGE_SIZE
            response = self.client.get(self.url, {'page_size': MAX_PAGE_SIZE + 500})
            
            # Verify Paginator was called with MAX_PAGE_SIZE (clamped)
            args = mock_paginator.call_args[0]
            self.assertEqual(args[1], MAX_PAGE_SIZE)
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_handles_invalid_page_gracefully(self, mock_objects):
        """Test that API handles invalid page numbers gracefully."""
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = []
            
            # Test with invalid page values
            for invalid_page in ['abc', '-1', '999999']:
                response = self.client.get(self.url, {'page': invalid_page})
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.content)
                # Should default to page 1
                self.assertEqual(data['page'], 1)
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_filters_by_sector(self, mock_objects):
        """Test that API correctly filters by sector."""
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = []
            
            response = self.client.get(self.url, {'sector': 'Primary'})
            
            # Verify filter was called
            mock_qs.filter.assert_called_once_with(Sector='Primary')
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_filters_by_multiple_schools(self, mock_objects):
        """Test that API correctly filters by multiple school names."""
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = []
            
            response = self.client.get(
                self.url + '?schools=School1&schools=School2&schools=School3'
            )
            
            # Verify filter was called with list
            call_args = mock_qs.filter.call_args
            self.assertIn('Name__in', call_args[1])
            self.assertEqual(len(call_args[1]['Name__in']), 3)
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_sorting(self, mock_objects):
        """Test that API correctly applies sorting."""
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = []
            
            # Test ascending sort
            response = self.client.get(self.url, {'sort': 'Name', 'order': 'asc'})
            mock_qs.order_by.assert_called_with('Name')
            
            # Test descending sort
            mock_qs.reset_mock()
            mock_paginator.reset_mock()
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            response = self.client.get(self.url, {'sort': 'Sector', 'order': 'desc'})
            mock_qs.order_by.assert_called_with('-Sector')
    
    @patch('home.views.SchoolRoll.objects')
    def test_data_api_prevents_sql_injection_in_sort(self, mock_objects):
        """Test that API rejects invalid column names in sort parameter."""
        mock_qs = MagicMock()
        mock_objects.using.return_value.all.return_value = mock_qs
        
        with patch('home.views.Paginator') as mock_paginator:
            mock_page = MagicMock()
            mock_page.object_list = []
            mock_page.number = 1
            mock_paginator.return_value.count = 0
            mock_paginator.return_value.num_pages = 1
            mock_paginator.return_value.page.return_value = mock_page
            
            mock_objects.using.return_value.order_by.return_value.values_list.return_value.distinct.return_value = []
            
            # Try to inject malicious SQL
            response = self.client.get(self.url, {'sort': 'Name; DROP TABLE--'})
            
            # Should not call order_by with invalid column
            if mock_qs.order_by.called:
                # If called, it should only be with valid columns
                call_args = str(mock_qs.order_by.call_args)
                self.assertNotIn('DROP', call_args)
                self.assertNotIn(';', call_args)


class EnrollmentGraphTests(TestCase):
    """Test cases for the enrollment_graph endpoint."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.url = reverse('enrollment_graph')
    
    @patch('home.views._create_empty_graph')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_graph_returns_placeholder_when_no_selection(self, mock_close, mock_savefig, mock_empty):
        """Test that graph returns placeholder when no schools selected."""
        mock_fig = MagicMock()
        mock_empty.return_value = mock_fig
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertEqual(response['Cache-Control'], 'no-cache')
        mock_empty.assert_called_once()
    
    @patch('home.views._fetch_enrollment_data')
    @patch('home.views._plot_enrollment_data')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_graph_accepts_ids_parameter(self, mock_close, mock_savefig, mock_plot, mock_fetch):
        """Test that graph endpoint accepts ObjectId parameters."""
        mock_fig = MagicMock()
        mock_plot.return_value = mock_fig
        mock_fetch.return_value = MagicMock()
        
        response = self.client.get(self.url + '?ids=1&ids=2&ids=3')
        
        self.assertEqual(response.status_code, 200)
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]  # positional args, not kwargs
        self.assertEqual(call_args[0], ['1', '2', '3'])  # first positional arg is selected_ids
    
    @patch('home.views._fetch_enrollment_data')
    @patch('home.views._plot_enrollment_data')
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_graph_accepts_schools_parameter(self, mock_close, mock_savefig, mock_plot, mock_fetch):
        """Test that graph endpoint accepts school name parameters."""
        mock_fig = MagicMock()
        mock_plot.return_value = mock_fig
        mock_fetch.return_value = MagicMock()
        
        response = self.client.get(self.url + '?schools=School1&schools=School2')
        
        self.assertEqual(response.status_code, 200)
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]  # positional args
        self.assertEqual(call_args[0], [])  # selected_ids is empty list
        self.assertEqual(call_args[1], ['School1', 'School2'])  # selected_schools
    
    @patch('home.views.SchoolRoll.objects')
    def test_fetch_enrollment_data_limits_schools(self, mock_objects):
        """Test that _fetch_enrollment_data enforces MAX_SCHOOLS_PER_GRAPH limit."""
        from home.views import _fetch_enrollment_data
        
        # Create list exceeding MAX_SCHOOLS_PER_GRAPH
        many_ids = [str(i) for i in range(MAX_SCHOOLS_PER_GRAPH + 20)]
        
        mock_qs = MagicMock()
        mock_objects.using.return_value.filter.return_value = mock_qs
        
        result = _fetch_enrollment_data(selected_ids=many_ids)
        
        # Verify filter was called with limited list
        call_args = mock_objects.using.return_value.filter.call_args
        filtered_ids = call_args[1]['ObjectId__in']
        self.assertEqual(len(filtered_ids), MAX_SCHOOLS_PER_GRAPH)
    
    def test_plot_uses_correct_color_palette(self):
        """Test that plotting uses colors from GRAPH_COLOR_PALETTE."""
        from home.views import _plot_enrollment_data
        
        # Create mock queryset with schools
        mock_schools = []
        for i in range(3):
            school = MagicMock()
            school.Name = f'School {i}'
            for year in YEARS:
                setattr(school, f'F{year}', 100 + i * 10)
            mock_schools.append(school)
        
        with patch('matplotlib.pyplot.subplots') as mock_subplots:
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)
            
            with patch('matplotlib.pyplot.rc_context'):
                fig = _plot_enrollment_data(mock_schools)
                
                # Verify plot was called with colors from palette
                self.assertEqual(mock_ax.plot.call_count, 3)
                for idx, call in enumerate(mock_ax.plot.call_args_list):
                    kwargs = call[1]
                    expected_color = GRAPH_COLOR_PALETTE[idx % len(GRAPH_COLOR_PALETTE)]
                    self.assertEqual(kwargs['color'], expected_color)


class IntegrationTests(TestCase):
    """Integration tests for the full application flow."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_index_page_loads(self):
        """Test that the index page loads successfully."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome')
    
    def test_data_page_loads(self):
        """Test that the data page loads successfully."""
        response = self.client.get(reverse('data_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'School Rolls Data')
        self.assertContains(response, 'data-page.js')
    
    def test_data_page_includes_filter_elements(self):
        """Test that data page includes all filter UI elements."""
        response = self.client.get(reverse('data_page'))
        
        self.assertContains(response, 'nameFilterList')
        self.assertContains(response, 'sectorFilterList')
        self.assertContains(response, 'typeFilterList')
        self.assertContains(response, 'selectAllSchools')
        self.assertContains(response, 'graph-content')


class ConstantsTests(TestCase):
    """Test cases for constants configuration."""
    
    def test_years_range_is_correct(self):
        """Test that YEARS constant has correct range."""
        self.assertEqual(YEARS[0], 1996)
        self.assertEqual(YEARS[-1], 2018)
        self.assertEqual(len(YEARS), 23)
    
    def test_pagination_constants_are_valid(self):
        """Test that pagination constants have valid values."""
        self.assertGreater(DEFAULT_PAGE_SIZE, 0)
        self.assertGreater(MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE)
        self.assertGreater(MAX_SCHOOLS_PER_GRAPH, 0)
    
    def test_color_palette_has_colors(self):
        """Test that GRAPH_COLOR_PALETTE is not empty."""
        self.assertGreater(len(GRAPH_COLOR_PALETTE), 0)
        # Verify all colors are hex format
        for color in GRAPH_COLOR_PALETTE:
            self.assertTrue(color.startswith('#'))
            self.assertEqual(len(color), 7)  # #RRGGBB
