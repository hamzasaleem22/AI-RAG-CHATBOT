import unittest
from unittest.mock import MagicMock, patch, ANY
import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Mock chromadb and sentence_transformers at the module level
# This ensures that when rag_system, vector_store, etc. are imported, they get the mock
mock_chromadb = MagicMock()
mock_sentence_transformers = MagicMock()

# Explicitly create a mock for SentenceTransformer class within the mocked module
mock_sentence_transformers.SentenceTransformer.return_value = MagicMock()

# Patch sys.modules to replace the actual modules with our mocks
with patch.dict(sys.modules, {
    'chromadb': mock_chromadb,
    'chromadb.config': mock_chromadb.config,
    'chromadb.utils.embedding_functions': mock_chromadb.utils.embedding_functions,
    'sentence_transformers': mock_sentence_transformers
}):
    # Now import the modules that depend on chromadb/sentence_transformers
    from backend.rag_system import RAGSystem
    from backend.vector_store import SearchResults # Assuming SearchResults is still needed and doesn't cause issues

    class TestRAGSystem(unittest.TestCase):

        @patch('backend.rag_system.DocumentProcessor')
        @patch('backend.rag_system.VectorStore')
        @patch('backend.rag_system.AIGenerator')
        @patch('backend.rag_system.SessionManager')
        @patch('backend.rag_system.ToolManager')
        @patch('backend.rag_system.CourseSearchTool')
        def setUp(self, MockCourseSearchTool, MockToolManager, MockSessionManager, MockAIGenerator, MockVectorStore, MockDocumentProcessor):
            """Set up a mock RAGSystem for each test"""
            
            self.mock_config = MagicMock()
            self.mock_config.CHUNK_SIZE = 1000
            self.mock_config.CHUNK_OVERLAP = 200
            self.mock_config.CHROMA_PATH = "/tmp/chroma"
            self.mock_config.EMBEDDING_MODEL = "mock-model"
            self.mock_config.MAX_RESULTS = 5
            self.mock_config.ANTHROPIC_API_KEY = "mock-key"
            self.mock_config.ANTHROPIC_MODEL = "mock-model"
            self.mock_config.MAX_HISTORY = 5

            # Instantiate mocks
            self.mock_doc_processor = MockDocumentProcessor.return_value
            self.mock_vector_store = MockVectorStore.return_value
            self.mock_ai_generator = MockAIGenerator.return_value
            self.mock_session_manager = MockSessionManager.return_value
            self.mock_tool_manager = MockToolManager.return_value
            self.mock_search_tool = MockCourseSearchTool.return_value

            # Create an instance of the RAGSystem
            self.rag_system = RAGSystem(self.mock_config)
            
            # Override the components with mocks
            self.rag_system.document_processor = self.mock_doc_processor
            self.rag_system.vector_store = self.mock_vector_store
            self.rag_system.ai_generator = self.mock_ai_generator
            self.rag_system.session_manager = self.mock_session_manager
            self.rag_system.tool_manager = self.mock_tool_manager
            self.rag_system.search_tool = self.mock_search_tool


        def test_query_with_tool_call(self):
            """Test a query that should trigger a tool call and succeed"""
            # Arrange
            query = "What is lesson 1 about?"
            session_id = "test_session_123"
            
            # Mock session history
            self.mock_session_manager.get_conversation_history.return_value = "Previous conversation"
            
            # Mock AI generator to return a response that uses a tool
            self.mock_ai_generator.generate_response.return_value = "The answer is based on search results."
            
            # Mock tool manager to return sources
            self.mock_tool_manager.get_last_sources.return_value = ["Source 1"]

            # Act
            answer, sources = self.rag_system.query(query, session_id)

            # Assert
            # Verify that the session manager was used
            self.mock_session_manager.get_conversation_history.assert_called_once_with(session_id)
            self.mock_session_manager.add_exchange.assert_called_once_with(session_id, query, answer)
            
            # Verify that the AI generator was called correctly
            self.mock_ai_generator.generate_response.assert_called_once_with(
                query=ANY,
                conversation_history="Previous conversation",
                tools=self.mock_tool_manager.get_tool_definitions.return_value,
                tool_manager=self.mock_tool_manager
            )
            
            # Verify that sources were retrieved and reset
            self.mock_tool_manager.get_last_sources.assert_called_once()
            self.mock_tool_manager.reset_sources.assert_called_once()
            
            # Verify the final output
            self.assertEqual(answer, "The answer is based on search results.")
            self.assertEqual(sources, ["Source 1"])

        def test_query_without_tool_call(self):
            """Test a query that should be answered directly without tools"""
            # Arrange
            query = "Hello, how are you?"
            session_id = "test_session_456"

            self.mock_session_manager.get_conversation_history.return_value = None
            self.mock_ai_generator.generate_response.return_value = "I am a helpful AI assistant."
            self.mock_tool_manager.get_last_sources.return_value = []
            
            # Act
            answer, sources = self.rag_system.query(query, session_id)
            
            # Assert
            self.mock_ai_generator.generate_response.assert_called_once()
            self.assertEqual(answer, "I am a helpful AI assistant.")
            self.assertEqual(sources, [])
            self.mock_tool_manager.get_last_sources.assert_called_once()
            self.mock_tool_manager.reset_sources.assert_called_once()

if __name__ == '__main__':
    unittest.main()