# Web Search Preference Toggle Component

## Overview
A React component that allows users to toggle between local/free and paid web search modes for agents.

## Location
`frontend/src/components/agents/config/web-search-preference-toggle.tsx`

## Features
- ✅ Toggle switch between Local/Free and Paid API modes
- ✅ Visual cards showing tools for each mode
- ✅ Cost information display
- ✅ Loading and error states
- ✅ Toast notifications for success/error
- ✅ Responsive design with dark mode support

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `agentId` | `string` | Yes | - | The ID of the agent to update |
| `currentPreference` | `'local' \| 'paid'` | No | `'local'` | Current web search preference |
| `onPreferenceChange` | `(newPreference: 'local' \| 'paid') => void` | No | - | Callback when preference changes |

## Usage

### Basic Usage
```tsx
import { WebSearchPreferenceToggle } from '@/components/agents/config';

function AgentSettings({ agentId }: { agentId: string }) {
  return (
    <WebSearchPreferenceToggle 
      agentId={agentId} 
    />
  );
}
```

### With Current Preference
```tsx
import { WebSearchPreferenceToggle } from '@/components/agents/config';
import { useState } from 'react';

function AgentSettings({ agentId }: { agentId: string }) {
  const [preference, setPreference] = useState<'local' | 'paid'>('local');
  
  return (
    <WebSearchPreferenceToggle 
      agentId={agentId}
      currentPreference={preference}
      onPreferenceChange={setPreference}
    />
  );
}
```

### With Callback Handler
```tsx
import { WebSearchPreferenceToggle } from '@/components/agents/config';

function AgentSettings({ agentId }: { agentId: string }) {
  const handlePreferenceChange = (newPreference: 'local' | 'paid') => {
    console.log('Preference changed to:', newPreference);
    // Perform additional actions like analytics, etc.
  };
  
  return (
    <WebSearchPreferenceToggle 
      agentId={agentId}
      onPreferenceChange={handlePreferenceChange}
    />
  );
}
```

## Web Search Modes

### Local/Free Mode
- **Search Tool:** DuckDuckGo (privacy-focused search engine)
- **Scraping Tool:** BeautifulSoup (web scraping and parsing)
- **Cost:** Free, unlimited usage
- **Requirements:** None

### Paid API Mode
- **Search Tool:** Tavily (~$0.005 per search request)
- **Scraping Tool:** Firecrawl (~$0.01 per page scraped)
- **Cost:** Pay-per-use from providers
- **Requirements:** API keys for Tavily and Firecrawl

## API Endpoint

The component calls the following API endpoint:

```
PUT /agents/{agentId}/web-search-preference
```

Request body:
```json
{
  "preference": "local" | "paid"
}
```

Response:
```json
{
  "success": true,
  "preference": "local" | "paid",
  "message": "Web search preference updated successfully"
}
```

## Toast Notifications

### Success
- **Title:** "Web search mode updated"
- **Description:** Shows which tools are now being used

### Error
- **Title:** "Failed to update preference"
- **Description:** Shows error message or "Please try again"

## Styling

The component uses:
- **shadcn/ui components:** Switch, Card, Badge
- **Tailwind CSS** for styling
- **Dark mode** support via Tailwind dark: classes
- **Responsive design** with mobile-friendly grid layout

## Dependencies

```json
{
  "lucide-react": "Icons",
  "sonner": "Toast notifications",
  "@/components/ui/switch": "Toggle switch component",
  "@/components/ui/card": "Card components",
  "@/components/ui/badge": "Badge component",
  "@/lib/api": "API functions",
  "@/lib/utils": "Utility functions"
}
```
