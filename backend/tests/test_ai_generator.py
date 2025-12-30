import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.ai_generator import AIGenerator
from backend.search_tools import ToolManager

class TestAIGenerator(unittest.TestCase):

    def setUp(self):
        """Set up the AI generator with a mock client"""
        self.mock_anthropic_client = MagicMock()
        
        # Since the AIGenerator is instantiated with a client, we patch the class
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_anthropic.return_value = self.mock_anthropic_client
            self.ai_generator = AIGenerator(api_key="fake_key", model="claude-3-opus-20240229")

    def test_generate_response_handles_tool_call(self):
        """Test that generate_response correctly handles a tool call"""
        # Arrange
        mock_tool_manager = MagicMock(spec=ToolManager)
        
        # Simulate a response from Claude that requests a tool call
        mock_tool_use_response = MagicMock()
        mock_tool_use_response.stop_reason = "tool_use"
        
        # The content of the response should be a list of blocks
        mock_content_block = MagicMock()
        mock_content_block.type = "tool_use"
        mock_content_block.name = "search_course_content"
        mock_content_block.id = "tool_use_123"
        mock_content_block.input = {"query": "test query"}
        mock_tool_use_response.content = [mock_content_block]
        
        self.mock_anthropic_client.messages.create.return_value = mock_tool_use_response
        
        # Simulate the final response after the tool result is sent back
        mock_final_response = MagicMock()
        type(mock_final_response).content = PropertyMock(return_value=[MagicMock(text="Final answer")])
        
        # Make the second call to create return the final response
        self.mock_anthropic_client.messages.create.side_effect = [
            mock_tool_use_response,
            mock_final_response
        ]
        
        # Mock the tool execution result
        mock_tool_manager.execute_tool.return_value = "Tool results"

        # Act
        response = self.ai_generator.generate_response(
            query="What is testing?",
            tools=[{"name": "search_course_content", "description": "A tool", "input_schema": {}}],
            tool_manager=mock_tool_manager
        )

        # Assert
        # Check that messages.create was called twice
        self.assertEqual(self.mock_anthropic_client.messages.create.call_count, 2)
        
        # Check that the tool manager was called correctly
        mock_tool_manager.execute_tool.assert_called_once_with(
            "search_course_content",
            query="test query"
        )
        
        # Get the arguments of the second call to messages.create
        final_call_args, final_call_kwargs = self.mock_anthropic_client.messages.create.call_args
        
        # Check that the tool results were included in the final message to Claude
        messages = final_call_kwargs["messages"]
        self.assertEqual(len(messages), 3) # user_query, assistant_tool_use, user_tool_result
        tool_result_message = messages[2]
        
        self.assertEqual(tool_result_message["role"], "user")
        self.assertIsInstance(tool_result_message["content"], list)
        self.assertEqual(tool_result_message["content"][0]["type"], "tool_result")
        self.assertEqual(tool_result_message["content"][0]["tool_use_id"], "tool_use_123")
        self.assertEqual(tool_result_message["content"][0]["content"], "Tool results")

        # Check that the final response is returned
        self.assertEqual(response, "Final answer")


    def test_generate_response_no_tool_call(self):
        """Test a direct response without any tool calls"""
        # Arrange
        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        type(mock_response).content = PropertyMock(return_value=[MagicMock(text="Direct answer")])

        self.mock_anthropic_client.messages.create.return_value = mock_response

        # Act
        response = self.ai_generator.generate_response(query="Hello")

        # Assert
        self.mock_anthropic_client.messages.create.assert_called_once()
        self.assertEqual(response, "Direct answer")


if __name__ == '__main__':
    unittest.main()