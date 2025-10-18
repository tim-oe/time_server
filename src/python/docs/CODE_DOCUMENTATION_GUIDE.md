# Code Documentation with Linting Disable Comments

This document explains how to use pylint and flake8 disable comments for comprehensive code documentation while maintaining code quality standards.

## Overview

When writing detailed documentation, especially for APIs, you often need to include comprehensive descriptions that exceed normal line length limits. The following techniques allow you to maintain detailed documentation while satisfying linting requirements.

## Techniques

### 1. Block-level Disable Comments

Use `# pylint: disable=line-too-long` before a block of code and `# noqa` at the end:

```python
# pylint: disable=line-too-long
@extend_schema(
    summary="Get current server time",
    description="Returns the current server time in ISO format with comprehensive timezone information including UTC offset and daylight saving time details",
    tags=["Time"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "current_time": {"type": "string", "format": "date-time"},
                "timezone": {"type": "string"},
                "unix_timestamp": {"type": "number", "format": "float"},
            },
        }
    },
)  # noqa
```

### 2. Function Documentation

For long function docstrings:

```python
def complex_api_function(param1: str, param2: int) -> dict:
    """
    This is a very long documentation string that exceeds the normal line length limits.
    It contains detailed information about the function including parameters, return values,
    examples, and comprehensive descriptions that would normally trigger line-too-long warnings.
    
    This approach is useful for:
    - API documentation strings
    - Detailed function descriptions
    - Complex parameter explanations
    - Example usage scenarios
    
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
```

### 3. Class Documentation

For comprehensive class documentation:

```python
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
    
    def example_method(self):
        """Short method docstring."""  # noqa
        pass
```

### 4. Inline Comments

For specific long lines:

```python
def example_function():
    """Short docstring."""  # noqa
    # This is a very long comment that would normally trigger line-too-long warnings  # pylint: disable=line-too-long
    return "example"
```

## Best Practices

### When to Use Disable Comments

✅ **Good uses:**
- API documentation strings
- Comprehensive function descriptions
- Complex parameter explanations
- Error message descriptions
- Example usage scenarios
- Configuration documentation

❌ **Avoid for:**
- Regular code logic
- Simple variable assignments
- Basic function calls
- Short comments

### Formatting Guidelines

1. **Place disable comments strategically:**
   - `# pylint: disable=line-too-long` before the block
   - `# noqa` at the end of the block

2. **Keep disable comments close to the code:**
   - Don't disable for entire files unless necessary
   - Use specific disable comments rather than broad ones

3. **Document why you're disabling:**
   - Add comments explaining why the disable is necessary
   - Consider if the code can be refactored instead

## Examples in Your Project

### API Views
```python
# pylint: disable=line-too-long
@extend_schema(
    summary="Get sensor temperature",
    description="Read temperature from a specific DS18B20 sensor with comprehensive error handling and validation",
    tags=["DS18B20 Sensors"],
    responses={
        200: {
            "type": "object",
            "properties": {
                "sensor_id": {"type": "string", "example": "28-0123456789ab"},
                "temperature_celsius": {"type": "number", "example": 25.5},
                "timestamp": {"type": "string", "format": "date-time"},
            },
        }
    },
)  # noqa
```

### Model Documentation
```python
class TimeEntry(models.Model):
    """
    Time entry model for tracking work sessions and time spent on various tasks.
    
    This model provides comprehensive time tracking capabilities including:
    - Start and end time recording
    - Automatic duration calculation
    - Description and categorization
    - Validation and error handling
    """  # noqa
    
    start_time = models.DateTimeField(
        help_text="The time when the work session started, automatically set when creating new entries"
    )  # noqa
```

## Integration with Format Script

The format script (`poetry run format`) respects these disable comments:

- **Black**: Will format code but respect disable comments
- **isort**: Will sort imports normally
- **flake8**: Will skip lines with `# noqa` comments

## Testing

You can test that your disable comments work by running:

```bash
# Run the format script
poetry run format

# Run individual tools
poetry run black .
poetry run isort .
poetry run flake8 .
```

## Summary

Using disable comments allows you to:
- Write comprehensive documentation
- Maintain code quality standards
- Provide detailed API descriptions
- Include extensive examples and explanations

Remember to use these techniques judiciously and only when the documentation truly benefits from being more detailed than standard line length limits allow.
