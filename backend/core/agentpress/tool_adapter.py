"""
Universal Tool Call Adapter

This adapter interceptor normalizes computer tasks and commands across all LLM models,
supporting both native function calling (OpenAI format) and XML-based tool calling.

The adapter ensures seamless operation regardless of:
- Model provider (OpenAI, Anthropic, Google, etc.)
- Tool calling format preference (native JSON vs XML)
- Model capabilities (function calling support or not)

Architecture:
1. Input Normalization: Converts any tool call format to a unified internal representation
2. Execution Layer: Executes tools using the normalized format
3. Output Formatting: Returns results in the format the model expects
"""

import json
import re
from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass
from core.utils.logger import logger


@dataclass
class NormalizedToolCall:
    """Unified representation of a tool call, regardless of source format."""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: Optional[str] = None
    source_format: Literal["native", "xml"] = "native"
    raw_call: Optional[Any] = None


@dataclass
class AdapterConfig:
    """Configuration for the tool adapter behavior."""
    enable_native: bool = True
    enable_xml: bool = True
    prefer_native: bool = True
    auto_detect: bool = True
    strict_mode: bool = False  # If True, only use explicitly supported formats


class ToolCallAdapter:
    """
    Universal adapter for tool calls across all models.
    
    Supports:
    - Native function calling (OpenAI, Anthropic tools format, etc.)
    - XML-based tool calling (universal fallback)
    - Automatic format detection
    - Bidirectional conversion
    """
    
    def __init__(self, config: Optional[AdapterConfig] = None):
        self.config = config or AdapterConfig()
        self._xml_pattern = re.compile(
            r'<function_calls>\s*<invoke\s+name=["\']([^"\']+)["\']>(.*?)</invoke>\s*</function_calls>',
            re.DOTALL
        )
        self._param_pattern = re.compile(
            r'<parameter\s+name=["\']([^"\']+)["\']>(.*?)</parameter>',
            re.DOTALL
        )
    
    def normalize_tool_calls(self, raw_input: Any) -> List[NormalizedToolCall]:
        """
        Normalize tool calls from any format to unified representation.
        
        Args:
            raw_input: Can be:
                - Native function calls (list of dicts with 'function' key)
                - XML string with tool calls
                - Already normalized tool calls
                
        Returns:
            List of NormalizedToolCall objects
        """
        if not raw_input:
            return []
        
        # Handle string input (likely XML)
        if isinstance(raw_input, str):
            return self._parse_xml_tool_calls(raw_input)
        
        # Handle list input (likely native function calls)
        if isinstance(raw_input, list):
            return self._parse_native_tool_calls(raw_input)
        
        # Handle single native function call
        if isinstance(raw_input, dict):
            normalized = self._parse_single_native_call(raw_input)
            return [normalized] if normalized else []
        
        logger.warning(f"Unsupported tool call format: {type(raw_input)}")
        return []
    
    def _parse_native_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[NormalizedToolCall]:
        """Parse native (OpenAI-style) function calls."""
        normalized = []
        
        for call in tool_calls:
            normalized_call = self._parse_single_native_call(call)
            if normalized_call:
                normalized.append(normalized_call)
        
        return normalized
    
    def _parse_single_native_call(self, call: Dict[str, Any]) -> Optional[NormalizedToolCall]:
        """Parse a single native function call."""
        try:
            # OpenAI format: {id, type: "function", function: {name, arguments}}
            if call.get('type') == 'function' and 'function' in call:
                func = call['function']
                tool_name = func.get('name')
                arguments = func.get('arguments', '{}')
                
                # Arguments might be string or dict
                if isinstance(arguments, str):
                    parameters = json.loads(arguments) if arguments else {}
                else:
                    parameters = arguments
                
                return NormalizedToolCall(
                    tool_name=tool_name,
                    parameters=parameters,
                    call_id=call.get('id'),
                    source_format="native",
                    raw_call=call
                )
            
            # Direct format: {name, arguments}
            elif 'name' in call:
                arguments = call.get('arguments', {})
                if isinstance(arguments, str):
                    parameters = json.loads(arguments) if arguments else {}
                else:
                    parameters = arguments
                
                return NormalizedToolCall(
                    tool_name=call['name'],
                    parameters=parameters,
                    call_id=call.get('id'),
                    source_format="native",
                    raw_call=call
                )
            
        except Exception as e:
            logger.error(f"Failed to parse native tool call: {e}")
        
        return None
    
    def _parse_xml_tool_calls(self, xml_content: str) -> List[NormalizedToolCall]:
        """Parse XML-based tool calls."""
        normalized = []
        
        # Find all function_calls blocks
        matches = self._xml_pattern.finditer(xml_content)
        
        for match in matches:
            tool_name = match.group(1)
            params_xml = match.group(2)
            
            # Extract parameters
            parameters = {}
            param_matches = self._param_pattern.finditer(params_xml)
            
            for param_match in param_matches:
                param_name = param_match.group(1)
                param_value = param_match.group(2).strip()
                
                # Try to parse JSON values
                try:
                    parameters[param_name] = json.loads(param_value)
                except:
                    # Keep as string if not valid JSON
                    parameters[param_name] = param_value
            
            normalized.append(NormalizedToolCall(
                tool_name=tool_name,
                parameters=parameters,
                source_format="xml",
                raw_call=match.group(0)
            ))
        
        return normalized
    
    def to_native_format(self, normalized_calls: List[NormalizedToolCall]) -> List[Dict[str, Any]]:
        """
        Convert normalized tool calls to native (OpenAI-style) format.
        
        Returns:
            List of dicts in OpenAI function calling format
        """
        native_calls = []
        
        for call in normalized_calls:
            native_call = {
                'id': call.call_id or f"call_{hash(call.tool_name)}",
                'type': 'function',
                'function': {
                    'name': call.tool_name,
                    'arguments': json.dumps(call.parameters)
                }
            }
            native_calls.append(native_call)
        
        return native_calls
    
    def to_xml_format(self, normalized_calls: List[NormalizedToolCall]) -> str:
        """
        Convert normalized tool calls to XML format.
        
        Returns:
            XML string with function_calls
        """
        if not normalized_calls:
            return ""
        
        xml_parts = ["<function_calls>"]
        
        for call in normalized_calls:
            xml_parts.append(f'<invoke name="{call.tool_name}">')
            
            for param_name, param_value in call.parameters.items():
                # Serialize complex values as JSON
                if isinstance(param_value, (dict, list)):
                    value_str = json.dumps(param_value)
                else:
                    value_str = str(param_value)
                
                xml_parts.append(f'<parameter name="{param_name}">{value_str}</parameter>')
            
            xml_parts.append('</invoke>')
        
        xml_parts.append('</function_calls>')
        
        return '\n'.join(xml_parts)
    
    def detect_format(self, content: Any) -> Literal["native", "xml", "unknown"]:
        """
        Detect the format of tool calls in the content.
        
        Returns:
            "native", "xml", or "unknown"
        """
        if isinstance(content, str):
            if '<function_calls>' in content and '<invoke' in content:
                return "xml"
        
        if isinstance(content, (list, dict)):
            # Check for native format signatures
            if isinstance(content, list) and len(content) > 0:
                first = content[0]
                if isinstance(first, dict) and ('function' in first or 'name' in first):
                    return "native"
            elif isinstance(content, dict) and ('function' in content or 'name' in content):
                return "native"
        
        return "unknown"
    
    def adapt_for_model(self, 
                       normalized_calls: List[NormalizedToolCall],
                       model_supports_native: bool,
                       prefer_format: Optional[Literal["native", "xml"]] = None) -> Union[List[Dict], str]:
        """
        Adapt normalized tool calls to the best format for a specific model.
        
        Args:
            normalized_calls: The normalized tool calls to adapt
            model_supports_native: Whether the model supports native function calling
            prefer_format: Optional format preference override
            
        Returns:
            Either a list of native function calls or an XML string
        """
        # Explicit preference override
        if prefer_format == "native" and (model_supports_native or not self.config.strict_mode):
            return self.to_native_format(normalized_calls)
        elif prefer_format == "xml":
            return self.to_xml_format(normalized_calls)
        
        # Auto-detect based on model capabilities
        if self.config.auto_detect:
            if model_supports_native and self.config.prefer_native:
                return self.to_native_format(normalized_calls)
            else:
                return self.to_xml_format(normalized_calls)
        
        # Default to XML for universal compatibility
        return self.to_xml_format(normalized_calls)


class CommandNormalizer:
    """
    Normalizes computer commands and tasks across different execution contexts.
    
    This ensures commands work consistently whether they're executed via:
    - Shell tools
    - Browser tools
    - File system tools
    - Custom MCP tools
    """
    
    @staticmethod
    def normalize_shell_command(command: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Normalize a shell command for execution.
        
        Returns:
            Dict with 'command', 'working_dir', 'env', etc.
        """
        normalized = {
            'command': command.strip(),
            'working_dir': context.get('working_dir') if context else None,
            'env': context.get('env', {}) if context else {},
            'timeout': context.get('timeout', 300) if context else 300
        }
        
        return normalized
    
    @staticmethod
    def normalize_file_operation(operation: str, path: str, content: Optional[str] = None,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Normalize file operations (read, write, delete, etc.)
        
        Args:
            operation: 'read', 'write', 'delete', 'list', etc.
            path: File or directory path
            content: Optional content for write operations
            context: Additional context
            
        Returns:
            Normalized operation dict
        """
        normalized = {
            'operation': operation.lower(),
            'path': path,
            'content': content,
            'encoding': context.get('encoding', 'utf-8') if context else 'utf-8',
            'create_dirs': context.get('create_dirs', True) if context else True
        }
        
        return normalized
    
    @staticmethod
    def normalize_browser_task(task: str, url: Optional[str] = None, 
                              selectors: Optional[List[str]] = None,
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Normalize browser automation tasks.
        
        Args:
            task: 'navigate', 'click', 'fill', 'screenshot', etc.
            url: Optional URL for navigation
            selectors: Optional CSS selectors
            context: Additional context
            
        Returns:
            Normalized task dict
        """
        normalized = {
            'task': task.lower(),
            'url': url,
            'selectors': selectors or [],
            'wait_for': context.get('wait_for') if context else None,
            'timeout': context.get('timeout', 30000) if context else 30000
        }
        
        return normalized


# Singleton instance for global access
_default_adapter = ToolCallAdapter()

def get_tool_adapter(config: Optional[AdapterConfig] = None) -> ToolCallAdapter:
    """Get or create a tool call adapter instance."""
    if config:
        return ToolCallAdapter(config)
    return _default_adapter
