# Voice Interface Components

Free browser-based voice input for Suna using the Web Speech API.

## Components

### 1. `EnhancedVoiceRecorder`

A compact voice recorder button for inline use in chat interfaces.

**Features:**
- 🎤 One-click voice recording
- 🔴 Visual recording indicator with pulsing animation
- 💬 Real-time transcript preview in tooltip
- ⚡ Instant transcription using browser's native speech recognition
- 🌍 Multi-language support
- 🆓 100% free - no API costs

**Usage:**

```tsx
import { EnhancedVoiceRecorder } from '@/components/voice';

function MyComponent() {
  const handleTranscription = (text: string) => {
    console.log('Transcribed:', text);
  };

  return (
    <EnhancedVoiceRecorder
      onTranscription={handleTranscription}
      lang="en-US"
      disabled={false}
    />
  );
}
```

**Props:**
- `onTranscription: (text: string) => void` - Callback when transcription completes
- `disabled?: boolean` - Disable the recorder
- `lang?: string` - Language code (default: 'en-US')
- `className?: string` - Additional CSS classes

### 2. `VoiceControls`

A full-featured voice control panel with language selection and TTS toggle.

**Features:**
- 🎤 Voice input with visual feedback
- 🔊 Text-to-Speech toggle (for future TTS integration)
- 🌐 Language selector (10+ languages)
- 📝 Live transcript display
- ⚠️ Error handling and user feedback
- 🎨 Compact and full mode

**Usage:**

```tsx
import { VoiceControls } from '@/components/voice';

function MyComponent() {
  return (
    <VoiceControls
      onTranscriptionComplete={(text) => console.log(text)}
      enabled={true}
      compact={false}
    />
  );
}
```

**Props:**
- `onTranscriptionComplete?: (text: string) => void` - Callback when transcription completes
- `enabled?: boolean` - Enable/disable voice input (default: true)
- `voiceEnabled?: boolean` - Enable/disable TTS (default: true)
- `className?: string` - Additional CSS classes
- `compact?: boolean` - Use compact mode (default: false)

### 3. `useVoiceInput` Hook

React hook for custom voice input implementations.

**Features:**
- 🔧 Full control over voice recognition
- 📊 Access to interim and final transcripts
- ❌ Error handling
- 🔄 Recording state management
- 🎛️ Configurable options

**Usage:**

```tsx
import { useVoiceInput } from '@/hooks/use-voice-input';

function MyComponent() {
  const {
    isRecording,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startRecording,
    stopRecording,
    resetTranscript,
  } = useVoiceInput({
    continuous: false,
    interimResults: true,
    lang: 'en-US',
    onTranscriptionComplete: (text) => console.log(text),
  });

  return (
    <div>
      <button onClick={startRecording} disabled={isRecording}>
        Start
      </button>
      <button onClick={stopRecording} disabled={!isRecording}>
        Stop
      </button>
      <p>{transcript}</p>
      <p className="italic">{interimTranscript}</p>
    </div>
  );
}
```

**Options:**
- `continuous?: boolean` - Keep recording after speech ends (default: false)
- `interimResults?: boolean` - Show results while speaking (default: true)
- `lang?: string` - Language code (default: 'en-US')
- `onTranscriptionComplete?: (transcript: string) => void` - Callback on completion

**Returns:**
- `isRecording: boolean` - Current recording state
- `transcript: string` - Final transcript
- `interimTranscript: string` - Interim transcript (while speaking)
- `error: string | null` - Error message if any
- `isSupported: boolean` - Browser support status
- `startRecording: () => void` - Start recording
- `stopRecording: () => void` - Stop recording
- `resetTranscript: () => void` - Clear transcript

## Supported Languages

- English (US) - `en-US`
- English (UK) - `en-GB`
- Spanish - `es-ES`
- French - `fr-FR`
- German - `de-DE`
- Italian - `it-IT`
- Portuguese - `pt-BR`
- Japanese - `ja-JP`
- Korean - `ko-KR`
- Chinese - `zh-CN`

## Browser Support

The Web Speech API is supported in:
- ✅ Chrome/Edge (full support)
- ✅ Safari 14.1+ (full support)
- ⚠️ Firefox (limited support, may require flag)
- ❌ IE (not supported)

The components automatically detect browser support and hide if unavailable.

## Integration with Chat Input

The `EnhancedVoiceRecorder` can be integrated into the existing chat input:

```tsx
// In chat-input.tsx
import { EnhancedVoiceRecorder } from '@/components/voice';

// Replace or complement the existing VoiceRecorder with:
<EnhancedVoiceRecorder
  onTranscription={handleTranscription}
  disabled={loading || (disabled && !isAgentRunning)}
  lang="en-US"
/>
```

## Error Handling

The components handle various error scenarios:

- **No speech detected** - User didn't speak
- **No microphone** - No audio input device found
- **Permission denied** - User blocked microphone access
- **Network error** - Connection issues
- **Not supported** - Browser doesn't support Web Speech API

## Performance

- **Zero API costs** - Uses browser's built-in speech recognition
- **Low latency** - Immediate transcription without server roundtrip
- **No file uploads** - No audio file creation or storage
- **Lightweight** - Minimal bundle size impact

## Privacy

- All processing happens in the browser
- No audio data sent to Suna servers
- Speech recognition handled by browser vendor (Google for Chrome, Apple for Safari)
- User must explicitly grant microphone permission

## Comparison with Existing VoiceRecorder

| Feature | VoiceRecorder (existing) | EnhancedVoiceRecorder (new) |
|---------|-------------------------|----------------------------|
| Cost | Uses backend transcription | FREE (browser-based) |
| Latency | Higher (upload + process) | Lower (instant) |
| File handling | Creates audio files | No files |
| Max duration | 15 minutes | Unlimited* |
| Languages | Backend dependent | 10+ languages |
| Offline | No | Limited** |
| Privacy | Server-side | Client-side |

\* Browser may have internal limits
\** Requires internet for recognition engine

## Future Enhancements

- [ ] Add Text-to-Speech output
- [ ] Voice command detection
- [ ] Custom wake words
- [ ] Voice activity detection
- [ ] Audio visualization
- [ ] Multi-language auto-detection
- [ ] Offline fallback to backend transcription
