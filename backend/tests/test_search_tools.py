
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Mock the VectorStore directly for CourseSearchTool tests
# This prevents importing the real VectorStore and its chromadb/sentence_transformers dependencies
from backend.search_tools import CourseSearchTool
# We still need SearchResults, so import it before the patch, or define a mock version if it also caused issues.
# Assuming SearchResults is a simple dataclass and doesn't directly trigger chromadb imports.
from backend.vector_store import SearchResults 

class TestCourseSearchTool(unittest.TestCase):

    def setUp(self):
        """Set up a mock vector store before each test"""
        # Mocking the VectorStore completely
        self.mock_vector_store = MagicMock()
        self.tool = CourseSearchTool(vector_store=self.mock_vector_store)

    def test_execute_success(self):
        """Test a successful search with filters"""
        # Arrange
        mock_results = SearchResults(
            documents=["doc1", "doc2"],
            metadata=[
                {"course_title": "Test Course", "lesson_number": 1},
                {"course_title": "Test Course", "lesson_number": 2}
            ],
            distances=[0.1, 0.2], # Added missing 'distances' argument
            error=None
        )
        self.mock_vector_store.search.return_value = mock_results
        
        # Act
        result = self.tool.execute(query="test query", course_name="Test Course", lesson_number=1)
        
        # Assert
        self.mock_vector_store.search.assert_called_once_with(
            query="test query",
            course_name="Test Course",
            lesson_number=1
        )
        self.assertIn("[Test Course - Lesson 1]", result)
        self.assertIn("doc1", result)
        self.assertEqual(len(self.tool.last_sources), 2)
        self.assertIn("Test Course - Lesson 1", self.tool.last_sources)

    def test_execute_no_results(self):
        """Test a search that returns no results"""
        # Arrange
        mock_results = SearchResults(documents=[], metadata=[], distances=[], error=None) # Added missing 'distances' argument
        self.mock_vector_store.search.return_value = mock_results
        
        # Act
        result = self.tool.execute(query="nonexistent query", course_name="No Course")
        
        # Assert
        self.assertEqual(result, "No relevant content found in course 'No Course'.")

    def test_execute_with_error(self):
        """Test a search that returns an error"""
        # Arrange
        mock_results = SearchResults(documents=[], metadata=[], distances=[], error="Vector store is offline") # Added missing 'distances' argument
        self.mock_vector_store.search.return_value = mock_results
        
        # Act
        result = self.tool.execute(query="any query")
        
        # Assert
        self.assertEqual(result, "Vector store is offline")

    def test_get_tool_definition(self):
        """Test that the tool definition is correct"""
        # Arrange
        definition = self.tool.get_tool_definition()
        
        # Assert
        self.assertEqual(definition["name"], "search_course_content")
        self.assertIn("query", definition["input_schema"]["properties"])
        self.assertIn("course_name", definition["input_schema"]["properties"])
        self.assertIn("lesson_number", definition["input_schema"]["properties"])
        self.assertEqual(definition["input_schema"]["required"], ["query"])

if __name__ == '__main__':
    unittest.main()
