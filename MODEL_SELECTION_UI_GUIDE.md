# Model Selection UI Guide

Visual guide for the model selection interface in Suna.

---

## 📍 Where to Find It

### 1. Agent Creation
**Location:** New Agent Dialog → Model Selection

```
┌────────────────────────────────────────┐
│ Create New Agent                    [x]│
├────────────────────────────────────────┤
│                                        │
│ Agent Name: [My Assistant...........]  │
│                                        │
│ Model:  [🦙 Llama 3.3 70B        ▼]  │  ← Model Selector
│                                        │
│ System Prompt:                         │
│ ┌────────────────────────────────────┐ │
│ │ You are a helpful assistant...     │ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
│                                        │
│           [Cancel]  [Create Agent]     │
└────────────────────────────────────────┘
```

### 2. Agent Settings
**Location:** Agent Configuration → Instructions Tab

```
┌────────────────────────────────────────┐
│ Agent Settings                      [x]│
├────────────────────────────────────────┤
│ [Instructions] [Tools] [Integrations]  │
├────────────────────────────────────────┤
│                                        │
│ Model:  [🦙 Llama 3.3 70B        ▼]  │  ← Change model
│                                        │
│ System Prompt:                         │
│ ┌────────────────────────────────────┐ │
│ │                                    │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

## 🎨 Model Selector Dropdown

### When Clicked

```
┌─────────────────────────────────────────────────┐
│ All Models                          [+] [🔑]    │
├─────────────────────────────────────────────────┤
│ 🔍 Search models...                             │
├─────────────────────────────────────────────────┤
│ Model                          Input    Output  │
├─────────────────────────────────────────────────┤
│ 🦙 Llama 3.3 70B              $0.00     $0.00  │ ← FREE
│ 🤖 Qwen 2.5 Coder             $0.00     $0.00  │ ← FREE
│ 🧠 DeepSeek R1 70B            $0.00     $0.00  │ ← FREE
│                                                 │
│ ──────────────────────────────────────────────  │
│ 👑 Premium Models                               │
│ ──────────────────────────────────────────────  │
│                                                 │
│ 🤖 Haiku 4.5                  $1.00     $5.00 👑│
│ 🤖 Sonnet 4                   $3.00    $15.00 👑│
│ 🤖 Sonnet 4.5                 $3.00    $15.00 👑│
│                                                 │
│ ┌────────────────────────────────────────────┐ │
│ │ 👑 Unlock all models + higher limits       │ │
│ │ [        Upgrade now        ]              │ │
│ └────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│ * All prices are per 1 million tokens          │
└─────────────────────────────────────────────────┘
```

**Icons:**
- `[+]` - Add custom model (local mode only)
- `[🔑]` - Local .env manager (local mode only)
- `👑` - Premium model (requires subscription)

---

## 💡 Model Information Display

### Hover Tooltip

```
┌─────────────────────────────────┐
│ Llama 3.3 70B                   │
├─────────────────────────────────┤
│ • Provider: Ollama              │
│ • Context: 128,000 tokens       │
│ • Cost: FREE (runs locally)     │
│ • Capabilities:                 │
│   - Chat                        │
│   - Function Calling            │
│                                 │
│ This model runs locally         │
│ on your machine using Ollama    │
└─────────────────────────────────┘
```

### Premium Model (Locked)

```
┌─────────────────────────────────┐
│ Claude Haiku 4.5                │
├─────────────────────────────────┤
│ Requires subscription to        │
│ access premium model            │
│                                 │
│ [Subscribe Now]                 │
└─────────────────────────────────┘
```

---

## 🎯 Usage Scenarios

### Scenario 1: Coding Assistant

**User Action:**  
Creates "Code Helper" agent

**Recommended Model:**  
`ollama/qwen2.5-coder` (FREE)

**UI Shows:**
```
Model: [🤖 Qwen 2.5 Coder        ▼]

💡 Tip: Optimized for code generation
   32K context window | FREE
```

### Scenario 2: General Assistant

**User Action:**  
Creates "Personal Assistant" agent

**Recommended Model:**  
`ollama/llama3.3` (FREE)

**UI Shows:**
```
Model: [🦙 Llama 3.3 70B         ▼]

💡 Tip: Best for general tasks
   128K context window | FREE
```

### Scenario 3: Complex Reasoning

**User Action:**  
Creates "Research Assistant" agent

**Recommended Model:**  
`ollama/deepseek-r1:70b` (FREE)  
or `anthropic/claude-sonnet-4-5` (PREMIUM)

**UI Shows:**
```
Model: [🧠 DeepSeek R1 70B       ▼]

💡 Tip: Excels at complex reasoning
   64K context window | FREE
```

---

## 🎨 Color Scheme

### Free Models
- Background: Default
- Text: Default
- Icon: Provider icon
- Badge: "FREE" in green

### Premium Models
- Background: Slightly muted
- Text: Default
- Icon: Provider icon + Crown 👑
- Badge: None (Crown indicates premium)

### Selected Model
- Background: Highlighted/Accented
- Border: Visible border
- Checkmark: ✓ on the right

---

## 📱 Responsive Design

### Desktop
```
┌─────────────────────────────────────────┐
│ Model: [🦙 Llama 3.3 70B          ▼]   │
│        Wide dropdown with all info      │
└─────────────────────────────────────────┘
```

### Mobile/Tablet
```
┌──────────────────────────┐
│ Model: [🦙 Llama 3.3  ▼]│
│        Compact layout     │
└──────────────────────────┘
```

---

## 🔍 Search Functionality

### Before Search
Shows all models in default order

### During Search: "llama"
```
┌─────────────────────────────────────────┐
│ 🔍 llama                                │
├─────────────────────────────────────────┤
│ 🦙 Llama 3.3 70B              $0.00    │
│                                         │
│ No other matches                        │
└─────────────────────────────────────────┘
```

### During Search: "free"
Shows only free models (filter by cost)

---

## ⚙️ Local Mode Features

### Add Custom Model

**Click [+] button:**

```
┌────────────────────────────────────┐
│ Add Custom Model                [x]│
├────────────────────────────────────┤
│                                    │
│ Model ID:                          │
│ [openai/gpt-4...................]  │
│                                    │
│ Display Name:                      │
│ [GPT-4...........................]  │
│                                    │
│ Note: Model must be available      │
│ in your environment                │
│                                    │
│        [Cancel]  [Add Model]       │
└────────────────────────────────────┘
```

### Custom Model in List

```
🤖 GPT-4 (Custom)         —      —    [✏️] [🗑️]
                                       ^    ^
                                      Edit Delete
```

---

## 🚀 Quick Actions

### Keyboard Shortcuts

- `↓` - Navigate down in model list
- `↑` - Navigate up in model list
- `Enter` - Select highlighted model
- `Esc` - Close dropdown
- Type to search

### Mouse Actions

- Click model → Select
- Hover → Show tooltip
- Click 👑 → Show upgrade dialog
- Click [+] → Add custom model
- Click [✏️] → Edit custom model
- Click [🗑️] → Delete custom model

---

## 📊 Status Indicators

### Model Status

```
✓ Available     - Model is accessible
👑 Premium      - Requires paid subscription
⚠️ Limited     - Performance may vary
🔒 Locked       - Upgrade required
```

### Agent Status

```
🟢 Active       - Agent is using this model
🔵 Default      - User's default model
⭐ Recommended  - Suggested for this use case
```

---

## 🎓 User Education

### First-Time User

**Shows tooltip:**
```
┌─────────────────────────────────────┐
│ 💡 New to model selection?          │
│                                     │
│ • FREE models run on your computer  │
│ • Premium models are in the cloud   │
│ • You can change models anytime     │
│                                     │
│ [Got it!]                          │
└─────────────────────────────────────┘
```

### Ollama Not Installed

**When ENV_MODE=local but no Ollama:**
```
┌─────────────────────────────────────┐
│ ⚠️ No FREE models available         │
│                                     │
│ Install Ollama to use free local    │
│ models like Llama 3.3               │
│                                     │
│ [Install Ollama]  [Use Premium]    │
└─────────────────────────────────────┘
```

---

## 🎯 Best Practices

### Do's ✅
- Show pricing clearly
- Indicate free vs premium
- Recommend appropriate models
- Allow easy model switching
- Provide search/filter

### Don'ts ❌
- Hide pricing until checkout
- Make premium models look free
- Force premium selections
- Prevent model changes
- Show disabled models without explanation

---

## 📱 Integration Points

### Where Model Selector Appears

1. **New Agent Dialog** - Primary creation flow
2. **Agent Settings** - Update existing agents
3. **Quick Settings** - Thread-level override
4. **Onboarding Flow** - First-time setup
5. **Agent Templates** - Pre-configured models

---

## Summary

The model selector UI provides:

✅ **Clear Pricing** - Show costs upfront  
✅ **Free Options** - Highlight Ollama models  
✅ **Easy Selection** - Intuitive dropdown  
✅ **Smart Defaults** - Based on user tier  
✅ **Search & Filter** - Find models quickly  
✅ **Upgrade Path** - Clear call-to-action  
✅ **Custom Models** - For advanced users  

**Result:** Users can easily choose the right model for their needs!
