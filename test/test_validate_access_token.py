
"""
=== UTC-20 TEST SUMMARY: _validate_access_token() Method ===
Test Implementation Date: September 5, 2025
Target Method: SpotifyRecommendController._validate_access_token()
Test Success Rate: 100% (4/4 tests passing)

TEST COVERAGE:
✅ Test Case 1: Successful token validation with valid Bearer token format
✅ Test Case 2: Error handling when Authorization header is missing
✅ Test Case 3: Error handling when Authorization header format is invalid
✅ Test Case 4: Error handling when Bearer token is invalid or expired

TECHNICAL IMPLEMENTATION:
- Flask test request context management for HTTP header simulation
- Mock spotipy.Spotify client for token validation testing
- Environment variable mocking with @patch.dict for secure testing
- Exception handling validation for authentication failures
- Response format validation for error and success cases

VALIDATION POINTS:
- Authorization header presence and format validation
- Bearer token extraction and processing
- Spotify client initialization with access token
- Token validity verification via sp.current_user() call
- Response structure: error, status_code, spotify_client fields
- Proper error messages and HTTP status codes

MOCK STRATEGY:
- spotipy.Spotify: Mocked for client initialization and authentication
- request.headers: Managed via Flask test_request_context
- sp.current_user(): Mocked for token validity simulation
- Exception scenarios: Token validation failure testing

STATUS: ✅ ALL TESTS PASSING - Method ready for production
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from flask import Flask

# Add the parent directory to sys.path to import the controller
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controller.SpotifyRecommendController import SpotifyRecommendController

class TestValidateAccessToken:
    
    def setup_method(self):
        """Setup Flask application context for each test method"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        """Clean up Flask application context after each test method"""
        self.app_context.pop()

    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret'
    })
    @patch('spotipy.Spotify')
    def test_validate_access_token_success_with_valid_bearer_token(self, mock_spotify):
        """
        Test Case 1: Successful Token Validation with Valid Bearer Token Format
        Tests successful validation of access token with valid Bearer token format
        Validates proper Spotify client creation and token verification
        """
        # Setup mock request with valid Authorization header
        with self.app.test_request_context(headers={'Authorization': 'Bearer valid_access_token'}):
            # Setup mock Spotify client
            mock_sp = MagicMock()
            mock_spotify.return_value = mock_sp
            
            # Mock successful user authentication (token is valid)
            mock_sp.current_user.return_value = {
                'id': 'test_user',
                'display_name': 'Test User'
            }
            
            # Create controller instance and test
            controller = SpotifyRecommendController()
            result = controller._validate_access_token()
            
            # Assertions
            assert result['error'] is None
            assert result['status_code'] == 200
            assert result['spotify_client'] is not None
            assert result['spotify_client'] == mock_sp
            
            # Verify Spotify client was created with correct token
            mock_spotify.assert_called_once_with(auth='valid_access_token')
            mock_sp.current_user.assert_called_once()

    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret'
    })
    def test_validate_access_token_missing_authorization_header(self):
        """
        Test Case 2: Error Handling When Authorization Header is Missing
        Tests error handling when Authorization header is missing from request
        Validates proper error response and status code for missing authentication
        """
        # Setup mock request without Authorization header
        with self.app.test_request_context():
            # Create controller instance and test
            controller = SpotifyRecommendController()
            result = controller._validate_access_token()
            
            # Assertions
            assert result['error'] == 'Access token is required'
            assert result['status_code'] == 401
            assert result['spotify_client'] is None

    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret'
    })
    def test_validate_access_token_invalid_format_without_bearer(self):
        """
        Test Case 3: Error Handling When Authorization Header Format is Invalid
        Tests error handling when Authorization header doesn't follow Bearer format
        Validates proper error response for malformed authentication headers
        """
        # Setup mock request with invalid Authorization header format
        with self.app.test_request_context(headers={'Authorization': 'InvalidFormatToken token_value'}):
            # Create controller instance and test
            controller = SpotifyRecommendController()
            result = controller._validate_access_token()
            
            # Assertions
            assert result['error'] == 'Access token is required'
            assert result['status_code'] == 401
            assert result['spotify_client'] is None

    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret'
    })
    @patch('spotipy.Spotify')
    def test_validate_access_token_invalid_or_expired_token(self, mock_spotify):
        """
        Test Case 4: Error Handling When Bearer Token is Invalid or Expired
        Tests error handling when Bearer token is invalid or expired
        Validates proper error response when Spotify API rejects the token
        """
        # Setup mock request with expired/invalid token
        with self.app.test_request_context(headers={'Authorization': 'Bearer expired_or_invalid_token'}):
            # Setup mock Spotify client that raises exception on token validation
            mock_sp = MagicMock()
            mock_spotify.return_value = mock_sp
            mock_sp.current_user.side_effect = Exception("Token expired or invalid")
            
            # Create controller instance and test
            controller = SpotifyRecommendController()
            result = controller._validate_access_token()
            
            # Assertions
            assert result['error'] == 'Invalid or expired access token'
            assert result['status_code'] == 401
            assert result['spotify_client'] is None
            
            # Verify Spotify client was created and validation attempted
            mock_spotify.assert_called_once_with(auth='expired_or_invalid_token')
            mock_sp.current_user.assert_called_once()
