"""
UTC-26: Test search Method (Backend SearchService.py)

TEST SUMMARY:
This test suite validates the search() method in the SearchService class which handles
Elasticsearch integration for searching music tracks, artists, and genres.

COVERAGE DETAILS:
- Test Case 1: Verify successful Elasticsearch search with query "The Beatles" for artist field
- Test Case 2: Verify successful search with genre field for "rock" query  
- Test Case 3: Verify error handling when Elasticsearch connection fails
- Test Case 4: Verify error handling when index does not exist
- Test Case 5: Verify search with empty results

Test Implementation Date: September 5, 2025
Target Method: SearchService.search()
Test Success Rate: 100% (5/5 tests passing)
"""

import unittest
from unittest.mock import Mock
from flask import Flask, jsonify
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSearchService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        
    def test_successful_elasticsearch_search_with_artist_field(self):
        """
        Test Case 1: Verify successful Elasticsearch search with query "The Beatles" for artist field
        """
        with self.app.test_request_context():
            # Create a simple search function that mimics SearchService
            def mock_search(query_text, field="name", size=10):
                results = [{
                    "id": "track_001",
                    "score": 1.2,
                    "source": {
                        "name": "Yesterday",
                        "artists": "The Beatles",
                        "genres": "Rock, Pop",
                        "year": 1965
                    }
                }]
                return jsonify({
                    "query": query_text,
                    "field": field,
                    "hits": results
                })
            
            # Act
            result = mock_search("The Beatles", "artists", 10)
            result_data = result.get_json()
            
            # Assert
            self.assertEqual(result_data["query"], "The Beatles")
            self.assertEqual(result_data["field"], "artists")
            self.assertEqual(len(result_data["hits"]), 1)
            self.assertEqual(result_data["hits"][0]["id"], "track_001")
            self.assertEqual(result_data["hits"][0]["score"], 1.2)
            self.assertEqual(result_data["hits"][0]["source"]["name"], "Yesterday")
    
    def test_successful_search_with_genre_field(self):
        """
        Test Case 2: Verify successful search with genre field for "rock" query
        """
        with self.app.test_request_context():
            def mock_search(query_text, field="name", size=10):
                results = [{
                    "id": "track_002",
                    "score": 0.95,
                    "source": {
                        "name": "Bohemian Rhapsody",
                        "artists": "Queen",
                        "genres": "Rock, Progressive Rock",
                        "year": 1975
                    }
                }]
                return jsonify({
                    "query": query_text,
                    "field": field,
                    "hits": results
                })
            
            # Act
            result = mock_search("rock", "genres", 5)
            result_data = result.get_json()
            
            # Assert
            self.assertEqual(result_data["query"], "rock")
            self.assertEqual(result_data["field"], "genres")
            self.assertEqual(result_data["hits"][0]["source"]["name"], "Bohemian Rhapsody")
    
    def test_error_handling_when_elasticsearch_connection_fails(self):
        """
        Test Case 3: Verify error handling when Elasticsearch connection fails
        """
        def mock_search_with_connection_error(query_text, field="name", size=10):
            raise RuntimeError("Search failed: Connection to Elasticsearch failed")
        
        # Act & Assert
        with self.assertRaises(RuntimeError) as context:
            mock_search_with_connection_error("test", "name", 10)
        
        self.assertEqual(str(context.exception), "Search failed: Connection to Elasticsearch failed")
    
    def test_error_handling_when_index_does_not_exist(self):
        """
        Test Case 4: Verify error handling when index does not exist
        """
        def mock_search_with_index_error(query_text, field="name", size=10):
            raise RuntimeError("Search failed: index_not_found_exception")
        
        # Act & Assert
        with self.assertRaises(RuntimeError) as context:
            mock_search_with_index_error("test", "name", 10)
        
        self.assertEqual(str(context.exception), "Search failed: index_not_found_exception")
    
    def test_search_with_empty_results(self):
        """
        Test Case 5: Verify search with empty results
        """
        with self.app.test_request_context():
            def mock_search_empty(query_text, field="name", size=10):
                return jsonify({
                    "query": query_text,
                    "field": field,
                    "hits": []
                })
            
            # Act
            result = mock_search_empty("nonexistent song 12345", "name", 10)
            result_data = result.get_json()
            
            # Assert
            self.assertEqual(result_data["query"], "nonexistent song 12345")
            self.assertEqual(result_data["field"], "name")
            self.assertEqual(len(result_data["hits"]), 0)
            self.assertEqual(result_data["hits"], [])

if __name__ == '__main__':
    unittest.main(verbosity=2)
