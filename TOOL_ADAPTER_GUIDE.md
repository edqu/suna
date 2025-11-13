# Universal Tool Call Adapter Guide

## Overview

The Universal Tool Call Adapter is an interceptor system that normalizes computer tasks and commands across all AI models, regardless of their native tool calling format or capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Model (Any Provider)                   │
│          OpenAI • Anthropic • Google • Ollama • etc          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Universal Tool Call Adapter                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Format Detection:                                   │    │
│  │  - Native (OpenAI JSON)  ✓                          │    │
│  │  - XML (<function_calls>) ✓                         │    │
│  │  - Auto-detect format    ✓                          │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Normalization:                                      │    │
│  │  All formats → NormalizedToolCall                    │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Output Adaptation:                                  │    │
│  │  NormalizedToolCall → Model's preferred format       │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Tool Execution Layer                            │
│  Shell • Files • Browser • Web Search • Vision • etc         │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Tool Call Adapter (`backend/core/agentpress/tool_adapter.py`)

The main adapter class that handles format conversion.

#### Key Classes:

**`NormalizedToolCall`** - Unified representation of a tool call:
```python
@dataclass
class NormalizedToolCall:
    tool_name: str                    # Name of the tool/function
    parameters: Dict[str, Any]        # Parameters as dict
    call_id: Optional[str]            # Unique call identifier
    source_format: "native" | "xml"   # Original format
    raw_call: Optional[Any]           # Original call data
```

**`ToolCallAdapter`** - Main adapter class:
- `normalize_tool_calls()` - Convert any format to NormalizedToolCall
- `to_native_format()` - Convert to OpenAI-style JSON
- `to_xml_format()` - Convert to XML format
- `detect_format()` - Auto-detect the format
- `adapt_for_model()` - Choose best format for a model

**`CommandNormalizer`** - Normalizes computer commands:
- `normalize_shell_command()` - Shell/terminal commands
- `normalize_file_operation()` - File system operations
- `normalize_browser_task()` - Browser automation tasks

### 2. Integration Points

**In `run.py` (lines 784-820)**:
```python
# Initialize adapter with model capabilities
adapter_config = AdapterConfig(
    enable_native=True,
    enable_xml=True,
    prefer_native=model_supports_native,
    auto_detect=True,
    strict_mode=False
)
tool_adapter = get_tool_adapter(adapter_config)
```

**In `response_processor.py` (lines 107-114)**:
```python
# Adapter initialized in ResponseProcessor
self.tool_adapter = get_tool_adapter()
```

## Supported Formats

### Native (OpenAI-style JSON)
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "execute_shell_command",
    "arguments": "{\"command\": \"ls -la\", \"working_dir\": \"/home\"}"
  }
}
```

### XML Format
```xml
<function_calls>
<invoke name="execute_shell_command">
<parameter name="command">ls -la</parameter>
<parameter name="working_dir">/home</parameter>
</invoke>
</function_calls>
```

## Usage Examples

### Example 1: Normalize Tool Calls from Any Model

```python
from core.agentpress.tool_adapter import get_tool_adapter

adapter = get_tool_adapter()

# From native format
native_calls = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "arguments": '{"query": "Python tutorials"}'
        }
    }
]

normalized = adapter.normalize_tool_calls(native_calls)
# Result: [NormalizedToolCall(tool_name='search_web', parameters={'query': 'Python tutorials'}, ...)]
```

### Example 2: Convert Between Formats

```python
# Convert normalized calls to XML
xml_output = adapter.to_xml_format(normalized)

# Convert normalized calls to native
native_output = adapter.to_native_format(normalized)
```

### Example 3: Auto-Adapt for Model

```python
# Automatically choose best format for a model
model_supports_native = True  # From model capabilities
output = adapter.adapt_for_model(
    normalized_calls,
    model_supports_native=model_supports_native
)
# Returns native format if supported, XML otherwise
```

### Example 4: Normalize Computer Commands

```python
from core.agentpress.tool_adapter import CommandNormalizer

# Normalize shell command
shell_cmd = CommandNormalizer.normalize_shell_command(
    "python script.py",
    context={'working_dir': '/app', 'timeout': 60}
)
# Result: {'command': 'python script.py', 'working_dir': '/app', 'env': {}, 'timeout': 60}

# Normalize file operation
file_op = CommandNormalizer.normalize_file_operation(
    "write",
    "/app/data.txt",
    content="Hello World"
)
# Result: {'operation': 'write', 'path': '/app/data.txt', 'content': 'Hello World', ...}
```

## Configuration

### AdapterConfig Options

```python
@dataclass
class AdapterConfig:
    enable_native: bool = True      # Allow native JSON format
    enable_xml: bool = True          # Allow XML format
    prefer_native: bool = True       # Prefer native when both supported
    auto_detect: bool = True         # Auto-detect format
    strict_mode: bool = False        # Only use explicitly supported formats
```

## Model Compatibility

| Model Provider | Native Support | XML Support | Recommended Format |
|----------------|---------------|-------------|-------------------|
| OpenAI         | ✅ Yes        | ✅ Yes      | Native            |
| Anthropic      | ✅ Yes        | ✅ Yes      | Native            |
| Google         | ✅ Yes        | ✅ Yes      | Native            |
| Ollama         | ⚠️ Varies     | ✅ Yes      | XML (universal)   |
| Other          | ⚠️ Unknown    | ✅ Yes      | XML (fallback)    |

**Legend:**
- ✅ Yes: Fully supported
- ⚠️ Varies: Depends on specific model
- XML: Universal fallback that works with ALL models

## Benefits

### 1. **Universal Compatibility**
- Works with ANY AI model, regardless of provider
- No model-specific code in tool implementations
- Automatic format detection and conversion

### 2. **Seamless Operation**
- Tools execute identically regardless of format
- No user-visible differences between formats
- Transparent format conversion

### 3. **Future-Proof**
- Easy to add new formats
- Model updates don't break existing tools
- New models work immediately

### 4. **Normalized Execution**
- Consistent command structure
- Unified error handling
- Predictable behavior across models

## How It Works

1. **Model Response** → AI model returns tool calls in its native format
2. **Detection** → Adapter detects the format (native JSON or XML)
3. **Normalization** → Converts to `NormalizedToolCall` internal format
4. **Execution** → Tools execute using normalized format
5. **Result** → Results returned in format model expects

## Testing

```python
# Test adapter with different formats
from core.agentpress.tool_adapter import ToolCallAdapter

adapter = ToolCallAdapter()

# Test native format parsing
native_test = adapter.normalize_tool_calls([
    {"type": "function", "function": {"name": "test", "arguments": "{}"}}
])
assert len(native_test) == 1
assert native_test[0].tool_name == "test"

# Test XML format parsing
xml_test = adapter.normalize_tool_calls(
    '<function_calls><invoke name="test"><parameter name="arg">value</parameter></invoke></function_calls>'
)
assert len(xml_test) == 1
assert xml_test[0].parameters["arg"] == "value"

# Test format conversion
xml_output = adapter.to_xml_format(native_test)
assert "<invoke name=\"test\">" in xml_output
```

## Troubleshooting

### Issue: Tool calls not detected
**Solution:** Check if both `enable_native` and `enable_xml` are True in config

### Issue: Wrong format used for model
**Solution:** Verify model capabilities detection in `run.py` lines 790-796

### Issue: Parameters not parsing correctly
**Solution:** Ensure parameters are valid JSON in native format, or properly escaped in XML

## Future Enhancements

- [ ] Add support for additional formats (e.g., YAML, custom formats)
- [ ] Implement caching for format conversions
- [ ] Add telemetry for format usage statistics
- [ ] Create format-specific optimizations
- [ ] Add validation schemas for all formats

## Related Files

- `backend/core/agentpress/tool_adapter.py` - Main adapter implementation
- `backend/core/run.py` - Adapter initialization and configuration
- `backend/core/agentpress/response_processor.py` - Integration with response processing
- `backend/core/agentpress/xml_tool_parser.py` - XML parsing utilities
- `backend/core/agentpress/tool_registry.py` - Tool registry system

## Support

For issues or questions:
1. Check the logs for adapter-related messages (look for "🔧 Universal Tool Adapter")
2. Verify model capabilities in the logs
3. Review the format detection output
4. Check `NormalizedToolCall` structure in debug logs
