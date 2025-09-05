import pytest
import os
from unittest.mock import patch, MagicMock
import sys
from flask import Flask

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from controller.SpotifyAuthController import SpotifyAuthController

class TestHandleCallback:
    
    def setup_method(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def teardown_method(self):
        self.app_context.pop()
    
    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'REDIRECT_URI': 'http://localhost:3000/callback'
    })
    def test_handle_callback_missing_code(self):
        # Test missing authorization code
        controller = SpotifyAuthController()
        
        with self.app.test_request_context('/'):
            result = controller.handle_callback()
            
            # Extract response data
            if isinstance(result, tuple):
                response, status_code = result
                assert status_code == 400
                data = response.get_json()
            else:
                data = result.get_json()
            
            assert data['success'] == False
            assert 'No authorization code received' in data['error']
    
    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'REDIRECT_URI': 'http://localhost:3000/callback'
    })
    def test_handle_callback_access_denied(self):
        # Test access denied error
        controller = SpotifyAuthController()
        
        with self.app.test_request_context('/?error=access_denied'):
            result = controller.handle_callback()
            
            # Extract response data
            if isinstance(result, tuple):
                response, status_code = result
                assert status_code == 400
                data = response.get_json()
            else:
                data = result.get_json()
            
            assert data['success'] == False
            assert 'Spotify authorization error: access_denied' in data['error']
    
    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'REDIRECT_URI': 'http://localhost:3000/callback'
    })
    def test_handle_callback_invalid_code(self):
        # Test invalid/expired code
        controller = SpotifyAuthController()
        
        with patch.object(controller.sp_oauth, 'get_access_token') as mock_get_token:
            mock_get_token.return_value = None
            
            with self.app.test_request_context('/?code=invalid_code'):
                result = controller.handle_callback()
                
                # Extract response data
                if isinstance(result, tuple):
                    response, status_code = result
                    assert status_code == 400
                    data = response.get_json()
                else:
                    data = result.get_json()
                
                assert data['success'] == False
                assert 'Failed to get access token' in data['error']
    
    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'REDIRECT_URI': 'http://localhost:3000/callback'
    })
    @patch('spotipy.Spotify')
    def test_handle_callback_success(self, mock_spotify):
        # Test successful callback processing
        controller = SpotifyAuthController()
        
        # Mock Spotify API
        mock_sp_instance = MagicMock()
        mock_spotify.return_value = mock_sp_instance
        mock_sp_instance.current_user.return_value = {
            'id': 'spotify_user_123',
            'display_name': 'John Doe',
            'email': 'john@example.com',
            'images': [],
            'followers': {'total': 150}
        }
        
        with patch.object(controller.sp_oauth, 'get_access_token') as mock_get_token:
            mock_get_token.return_value = {
                'access_token': 'BQC4WK3...',
                'refresh_token': 'AQD5xL2...',
                'expires_at': 1735456000
            }
            
            with self.app.test_request_context('/?code=valid_auth_code_12345'):
                result = controller.handle_callback()
                
                # Extract response data
                if isinstance(result, tuple):
                    response, status_code = result
                    data = response.get_json()
                else:
                    data = result.get_json()
                
                assert data['success'] == True
                assert 'access_token' in data
                assert data['access_token'] == 'BQC4WK3...'
                assert 'user' in data
                assert data['user']['id'] == 'spotify_user_123'

# === TEST SUMMARY ===
# Test ID: UTC-18 (handle_callback method)
# Total Test Cases: 4
# TESTED FUNCTIONALITY:
# 1. Missing authorization code handling
# 2. Access denied error handling  
# 3. Invalid/expired code handling
# 4. Successful token exchange and user profile retrieval
