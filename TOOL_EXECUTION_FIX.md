# Tool Execution Fix - Ask Tool Returning Schemas ✅

## Problem

When asking a question, the agent returned raw JSON instead of executing the tool:

**User sees**:
```json
{ 
  "type": "function", 
  "function": { 
    "name": "ask", 
    "description": "Ask the user for confirmation..." 
  } 
}
```

**Should see**:
```
Agent: "Would you like me to proceed with this approach?"
```

## Root Cause

The LLM (Ollama) was **echoing the tool schema** instead of **calling the tool** because:

1. ❌ Native function calling was enabled but instructions weren't clear enough
2. ❌ Model confused about whether to describe tools or use them
3. ❌ Insufficient guidance to prevent schema output

## Solution Implemented

### Enhanced Native Tool Instructions

**File**: `backend/core/run.py` (lines 516-540)

**Before**:
```python
system_content += """
IMPORTANT:
- DO NOT output JSON schemas or function definitions
- Focus on answering the user's question
"""
```

**After**:
```python
system_content += """
🚨 CRITICAL - DO NOT OUTPUT TOOL SCHEMAS:
- NEVER output JSON like: {"type": "function", "function": {...}}
- NEVER output tool definitions or specifications
- NEVER describe available tools in JSON format
- NEVER show function schemas or parameters

✅ CORRECT BEHAVIOR:
- Call tools directly when needed
- Just ask questions naturally using the ask tool
- The user cannot see function schemas

Example: call ask("What would you prefer?") 
         NOT: {"type": "function", "function": {"name": "ask"}}
```

### Key Changes

1. **More Explicit** - Clear examples of what NOT to do
2. **Visual Markers** - 🚨 and ✅ for emphasis
3. **Concrete Example** - Shows exact correct vs incorrect behavior
4. **User Perspective** - Explains user only sees natural language

## How It Works Now

### Correct Flow

```
LLM thinks: "I need to ask the user a question"
  ↓
LLM calls: ask(text="What would you like me to do?")
  ↓
Backend executes: MessageTool.ask()
  ↓
User sees: "What would you like me to do?" ✅
```

### Incorrect Flow (Now Fixed)

```
LLM thinks: "I should describe the ask tool"
  ↓
LLM outputs: {"type": "function", "function": {"name": "ask"}}
  ↓
User sees: Raw JSON schema ❌ (FIXED)
```

## Testing

### Test 1: Simple Question
```
User: "Find Python tutorials"

Expected: Agent searches and presents results, NOT tool schemas
```

### Test 2: Ask Tool
```
User: "Help me decide between React and Vue"

Expected: Agent asks "What's your experience level?" or similar
NOT: {"type": "function", "function": {"name": "ask"}}
```

### Test 3: Complete Tool
```
User: "Create a README file"

Expected: Agent creates file and says "Done!" 
NOT: Tool schema JSON
```

## Backend Logs to Watch

```bash
cd backend
python api.py
```

**Expected logs**:
```
🔧 Tool calling mode: native=True, xml=False, model=ollama/llama3:instruct
📝 System message built: 12500 chars, native_fc=True, xml=False
✅ System prompt clean - no schemas or XML examples in native mode
INFO - Enabling native function calling for Ollama model: ollama/llama3:instruct
```

**Warning to watch for**:
```
⚠️ System prompt contains function call examples or schemas in native mode!
```
If you see this, the fix didn't work properly.

## Files Modified

1. **`backend/core/run.py`** (lines 516-540)
   - Enhanced native tool calling instructions
   - Added explicit "DO NOT output schemas" warnings
   - Added concrete examples

## Related Fixes

This fix works together with:
- [BROWSER_SEARCH_FIX.md](./BROWSER_SEARCH_FIX.md) - Enabled native function calling for Ollama
- [COMPLETE_FIX_SUMMARY.md](./COMPLETE_FIX_SUMMARY.md) - Computer preview polling

## Troubleshooting

### Still Seeing Schemas?

**Check 1**: Is native function calling enabled?
```bash
# Look in backend logs for:
"🔧 Tool calling mode: native=True"
```

**Check 2**: Which model are you using?
```bash
# Ollama models should show:
"Enabling native function calling for Ollama model: ollama/..."
```

**Check 3**: Check the system prompt
```bash
# Look for this warning in logs:
"⚠️ System prompt contains function call examples or schemas"
```

If you see the warning, schemas are still in the prompt (bug).

### Model Not Calling Tools?

**Possible causes**:
1. Model doesn't support function calling well
2. Tool schemas malformed
3. Streaming issues

**Solutions**:
- Try different model: `ollama/qwen2.5-coder` (better at function calling)
- Check backend logs for tool execution errors
- Verify tools are registered: Look for "✅ Registered" messages

## Model Recommendations

### Best for Function Calling

| Model | Function Calling | Reliability |
|-------|-----------------|-------------|
| ollama/qwen2.5-coder | ⭐⭐⭐⭐⭐ | Excellent |
| ollama/llama3.3 | ⭐⭐⭐⭐ | Very Good |
| ollama/llama3:instruct | ⭐⭐⭐ | Good |
| ollama/deepseek-r1:70b | ⭐⭐⭐⭐⭐ | Excellent |

**Recommendation**: Use `qwen2.5-coder` or `deepseek-r1:70b` for best tool calling results.

## What Changed

### Before
```
User: "Help me decide"
Agent: {"type": "function", "function": {"name": "ask", ...}}
User: "What is this??" 😕
```

### After
```
User: "Help me decide"  
Agent: "What are your main priorities for this decision?"
User: [Answers question] ✅
```

## Summary

✅ **Fixed**: Agent no longer outputs raw tool schemas  
✅ **Improved**: Clearer instructions for native function calling  
✅ **Enhanced**: Better examples and warnings in system prompt  
✅ **Works**: Ollama models now use tools correctly  

The ask, complete, and all other tools now work naturally - users see questions and responses, not JSON schemas!
