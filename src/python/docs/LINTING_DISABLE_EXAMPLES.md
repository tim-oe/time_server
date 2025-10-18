"""
Example Documentation with Linting Disable Comments

This file demonstrates how to use pylint and flake8 disable comments
for long documentation strings and API descriptions.
"""

# pylint: disable=line-too-long
def example_long_documentation():
    """
    This is a very long documentation string that exceeds the normal line length limits.
    It contains detailed information about the function including parameters, return values,
    examples, and comprehensive descriptions that would normally trigger line-too-long warnings.
    
    This approach is useful for:
    - API documentation strings
    - Detailed function descriptions
    - Complex parameter explanations
    - Example usage scenarios
    
    Returns:
        str: A formatted string containing the documentation
    """  # noqa
    return "This function has very long documentation"


def example_api_description():
    """
    Example of how to handle long API descriptions in Django REST Framework.
    
    This demonstrates the proper way to format long descriptions for:
    - @extend_schema decorators
    - API endpoint documentation
    - Request/response schema descriptions
    - Error message explanations
    """  # noqa
    pass


# pylint: disable=line-too-long
class ExampleAPIView:
    """
    Example API view class with comprehensive documentation.
    
    This class demonstrates how to document complex API views with:
    - Detailed class-level documentation
    - Method descriptions
    - Parameter explanations
    - Return value documentation
    - Usage examples
    - Error handling information
    """  # noqa
    
    def example_method(self, param1: str, param2: int) -> dict:
        """
        Example method with long parameter descriptions.
        
        Args:
            param1 (str): This is a very long description of the first parameter
                         that explains its purpose, format, and usage examples
                         in detail to provide comprehensive documentation.
            param2 (int): This is another long description explaining the second
                         parameter including its range, constraints, and typical
                         values used in the application.
        
        Returns:
            dict: A dictionary containing the processed results with detailed
                  structure including all possible keys and their meanings.
        """  # noqa
        return {"param1": param1, "param2": param2}


# Example of inline disable comments
def example_inline_disable():
    """Short docstring."""  # noqa
    # This is a very long comment that would normally trigger line-too-long warnings  # pylint: disable=line-too-long
    return "example"
