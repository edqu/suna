# Tool Cost Analysis - External Dependencies & API Requirements

## Summary

This document analyzes all agent tools for external costs and API dependencies.

## Tool Categories by Cost

### 🟢 **FREE TOOLS** (No API Keys or External Costs)

These tools work out of the box with no external dependencies:

#### Core Tools (Always Free)
1. **Message Tool** - Send messages to user
2. **Expand Message Tool** - View full message content
3. **Task List Tool** - Manage agent tasks

#### Sandbox Tools (Requires Daytona - Has Free Tier)
4. **Shell Tool** (`sb_shell_tool`) - Execute shell commands
5. **Files Tool** (`sb_files_tool`) - File operations
6. **Expose Tool** (`sb_expose_tool`) - Expose local services
7. **Upload File Tool** (`sb_upload_file_tool`) - Upload files
8. **KB Tool** (`sb_kb_tool`) - Knowledge base operations
9. **Docs Tool** (`sb_docs_tool`) - Create/edit documents
10. **Presentation Tool** (`sb_presentation_tool`) - Create presentations
11. **Vision Tool** (`sb_vision_tool`) - Analyze images (uses LLM vision)
12. **Image Edit Tool** (`sb_image_edit_tool`) - Edit images
13. **Design Tool** (`sb_design_tool`) - Create designs

#### Browser Tool (Uses Gemini)
14. **Browser Tool** (`browser_tool`) - Web automation using local Stagehand
   - ⚠️ Requires `GEMINI_API_KEY` for AI-powered browser actions
   - ✅ Runs Stagehand locally (no Stagehand API costs)
   - ✅ Uses Playwright for browser automation
   - **Cost**: Gemini API usage (FREE if using Gemini 2.0 Flash)
   - **Note**: Stagehand uses vision models to understand web pages

#### Agent Builder Tools (FREE)
15. **Agent Config Tool** - Configure agents
16. **MCP Search Tool** - Search for MCP integrations
17. **Credential Profile Tool** - Manage credentials
18. **Trigger Tool** - Set up automation triggers
19. **Agent Creation Tool** - Create new agents

---

### 🟡 **PAID TOOLS** (Require API Keys with Costs)

These tools require external paid services:

#### Web Search & Scraping
1. **Web Search Tool** (`web_search_tool`)
   - **Required**: `TAVILY_API_KEY` (search) + `FIRECRAWL_API_KEY` (scraping)
   - **Tavily Pricing**: ~$1/1000 searches (has free tier: 1000 searches/month)
   - **Firecrawl Pricing**: Pay-per-scrape ($0.001-0.01 per page)
   - **Alternative**: Could use free search APIs (DuckDuckGo, SerpAPI free tier)

2. **Image Search Tool** (`image_search_tool`)
   - **Required**: `SERPER_API_KEY`
   - **Serper Pricing**: ~$50/month for 5K searches
   - **Alternative**: Could use Google Custom Search API (100 free searches/day)

#### Research Tools
3. **Paper Search Tool** (`paper_search_tool`)
   - **Required**: `SEMANTIC_SCHOLAR_API_KEY`
   - **Cost**: FREE! Semantic Scholar is free to use
   - ✅ **Actually FREE despite requiring API key**

4. **People Search Tool** (`people_search_tool`)
   - **Required**: `EXA_API_KEY`
   - **Exa Pricing**: $20-200/month depending on usage
   - **Alternative**: Could use LinkedIn API (free tier limited)

5. **Company Search Tool** (`company_search_tool`)
   - **Required**: `EXA_API_KEY`
   - **Exa Pricing**: $20-200/month depending on usage
   - **Alternative**: Could use Clearbit API (has free tier)

#### Data Providers
6. **Data Providers Tool** (`data_providers_tool`)
   - **Required**: `RAPID_API_KEY`
   - **RapidAPI Pricing**: Varies by API (many have free tiers)
   - Includes: Twitter, YouTube, Instagram, TikTok, LinkedIn, Yahoo Finance, etc.
   - **Alternative**: Direct API access to each service (often free)

#### Voice Calls (Development Only)
7. **Vapi Voice Tool** (`vapi_voice_tool`)
   - **Required**: `VAPI_PRIVATE_KEY`
   - **Vapi Pricing**: Pay-per-minute for voice calls
   - **Only enabled in non-production mode**

---

## Cost Breakdown by Use Case

### Minimal Setup (100% Free)
To run Suna with ZERO external costs:

**Required:**
- ✅ Gemini API Key (FREE - use Gemini 2.0 Flash)
- ✅ Supabase (FREE tier)
- ✅ Redis (FREE - local or cloud free tier)
- ✅ Daytona (FREE tier for sandbox)

**Free Tools Available (17/20 tools = 85%):**
- ✅ All core tools (message, task list, expand message)
- ✅ All sandbox tools (shell, files, kb, docs, presentations, vision, image edit, design)
- ✅ Browser tool (uses free Gemini 2.0 Flash for AI actions)
- ✅ Agent builder tools (config, MCP search, credentials, triggers, agent creation)
- ✅ Paper search (Semantic Scholar is FREE!)
- ✅ Local Ollama models (FREE, runs on your machine)

**What You CAN'T Do (3 paid tools):**
- ❌ Web search (requires Tavily + Firecrawl)
- ❌ Image search (requires Serper)
- ❌ Company/people search (requires Exa)
- ❌ Data providers (requires RapidAPI)

**Cost**: $0/month for 85% of all functionality! 🎉

### Recommended Setup ($10-20/month)
Add basic search capabilities:

**APIs to Add:**
1. **Tavily API** - $0 (1000 free searches/month)
2. **Firecrawl API** - ~$10/month (basic plan)
3. **Semantic Scholar** - FREE
4. **Total**: ~$10-20/month depending on usage

**Unlocks:**
- ✅ Web search
- ✅ Web scraping
- ✅ Academic paper search

### Full-Featured Setup ($50-100/month)
All tools enabled:

**Additional APIs:**
1. **Serper API** - $50/month (5K searches)
2. **Exa API** - $20-50/month
3. **RapidAPI** - $10-30/month (various API subscriptions)
4. **Total**: ~$80-150/month for heavy usage

---

## Free Alternatives to Consider

### For Web Search
**Current**: Tavily ($1/1000 after free tier)
**Alternatives**:
- DuckDuckGo API (Free, no API key)
- SerpAPI (100 free searches/day)
- Brave Search API (Free tier available)

### For Image Search
**Current**: Serper ($50/month)
**Alternatives**:
- Google Custom Search API (100 free/day)
- Bing Image Search API (Free tier: 1000/month)
- Unsplash API (Free, open source images only)

### For People/Company Search
**Current**: Exa ($20-200/month)
**Alternatives**:
- LinkedIn API (Limited free tier)
- Clearbit API (Free tier for basic lookups)
- Hunter.io (Free tier: 50 searches/month)

### For Data Providers
**Current**: RapidAPI (varies)
**Alternatives**:
- Direct API access (many free):
  - Twitter API v2 (Free tier)
  - YouTube Data API (Free: 10K units/day)
  - Reddit API (Free)

---

## Integration Status Check

### ✅ Properly Integrated (No External Costs)

1. **Browser Tool**
   - Uses local Stagehand server
   - No external API calls
   - All browser automation is local
   - **Cost**: $0

2. **Sandbox Tools**
   - Uses Daytona Cloud Sandboxes
   - **Daytona Free Tier**: Available
   - All file/shell operations are within sandbox
   - **Cost**: $0 (free tier) or ~$20/month (paid tier)

3. **Agent Builder Tools**
   - All database operations (Supabase)
   - No external API dependencies
   - **Cost**: $0

### ⚠️ Requires External Paid APIs

1. **Web Search Tool**
   - Requires: Tavily + Firecrawl APIs
   - **Minimum Cost**: $0 (free tiers) - $20/month (regular usage)

2. **Image Search Tool**
   - Requires: Serper API
   - **Cost**: $50/month

3. **People/Company Search**
   - Requires: Exa API
   - **Cost**: $20-200/month

4. **Data Providers**
   - Requires: RapidAPI subscriptions
   - **Cost**: $10-100/month depending on APIs

---

## Recommendations

### For Development/Personal Use
**FREE Setup:**
```env
GEMINI_API_KEY=your-key  # FREE
# Skip: TAVILY, FIRECRAWL, SERPER, EXA, RAPID_API
# You still get: sandbox, browser, docs, vision, agent builder
```

**Tools Available**: 14/20 tools (70%)
**Monthly Cost**: $0

### For Light Production
**Low-Cost Setup:**
```env
GEMINI_API_KEY=your-key  # FREE
TAVILY_API_KEY=your-key  # FREE tier: 1000/month
FIRECRAWL_API_KEY=your-key  # ~$10/month
SEMANTIC_SCHOLAR_API_KEY=your-key  # FREE
```

**Tools Available**: 17/20 tools (85%)
**Monthly Cost**: ~$10-20

### For Full Production
**All Tools:**
```env
# All API keys configured
```

**Tools Available**: 20/20 tools (100%)
**Monthly Cost**: ~$80-150 depending on usage

---

## Checking Your Current Setup

Run this command in your backend directory to see which tools are available:

```python
python -c "
from core.utils.config import config

tools_status = {
    'Web Search': bool(config.TAVILY_API_KEY and config.FIRECRAWL_API_KEY),
    'Image Search': bool(config.SERPER_API_KEY),
    'Paper Search': bool(config.SEMANTIC_SCHOLAR_API_KEY),
    'People Search': bool(config.EXA_API_KEY),
    'Company Search': bool(config.EXA_API_KEY),
    'Data Providers': bool(config.RAPID_API_KEY),
    'Voice Calls': bool(config.VAPI_PRIVATE_KEY),
}

print('Tool Availability:')
for tool, available in tools_status.items():
    status = '✅ Available' if available else '❌ Not configured'
    print(f'{tool}: {status}')
"
```

---

## Cost Optimization Tips

1. **Use free tiers first**: Tavily, Firecrawl, Semantic Scholar all have free tiers
2. **Skip optional tools**: Image search, company search are nice-to-have
3. **Use Ollama**: Free local models with no API costs
4. **Monitor usage**: Set up usage alerts in your API dashboards
5. **Consider alternatives**: Many paid APIs have free alternatives

---

## Bottom Line

**Minimum cost to run Suna with basic functionality: $0/month**
- Use Gemini (free)
- Use free tool tiers
- Skip premium search tools

**Recommended setup for full functionality: ~$10-20/month**
- Gemini (free) or Anthropic ($20/month for moderate use)
- Tavily free tier + Firecrawl basic ($10/month)
- Skip expensive tools (Serper, Exa)

**All tools enabled: ~$80-150/month**
- Only if you need image search, company research, and data providers
