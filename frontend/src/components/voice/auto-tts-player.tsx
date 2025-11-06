'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Volume2, VolumeX, Pause, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useAutoTTS } from '@/hooks/use-auto-tts';
import { UnifiedMessage } from '@/components/thread/types';

export interface AutoTTSPlayerProps {
  messages: UnifiedMessage[];
  enabled?: boolean;
  className?: string;
}

/**
 * AutoTTSPlayer - Automatically speaks agent responses
 * 
 * Watches for new assistant messages and speaks them using browser TTS (FREE).
 * Shows a toggle button to enable/disable voice output.
 */
export const AutoTTSPlayer: React.FC<AutoTTSPlayerProps> = ({
  messages,
  enabled: initialEnabled = false,
  className,
}) => {
  const [ttsEnabled, setTtsEnabled] = useState(initialEnabled);
  const lastSpokenMessageId = useRef<string | null>(null);
  const hasInitialized = useRef(false);

  // Initialize TTS
  const {
    speak,
    stop,
    pause,
    resume,
    isSpeaking,
    isSupported,
    isEnabled,
  } = useAutoTTS({
    enabled: ttsEnabled,
    rate: 1.1, // Slightly faster than normal
    pitch: 1.0,
    volume: 1.0,
    lang: 'en-US',
  });

  // Watch for new assistant messages and speak them
  useEffect(() => {
    if (!ttsEnabled || !isSupported || messages.length === 0) {
      return;
    }

    // Skip first render to avoid speaking old messages
    if (!hasInitialized.current) {
      hasInitialized.current = true;
      // Set last spoken to the most recent message to avoid speaking history
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && lastMessage.type === 'assistant') {
        lastSpokenMessageId.current = lastMessage.message_id;
      }
      return;
    }

    // Find new assistant messages that haven't been spoken
    const newAssistantMessages = messages.filter((msg) => {
      // Only process assistant messages
      if (msg.type !== 'assistant') return false;
      
      // Skip if already spoken
      if (lastSpokenMessageId.current && msg.message_id) {
        const currentIndex = messages.findIndex(m => m.message_id === lastSpokenMessageId.current);
        const msgIndex = messages.findIndex(m => m.message_id === msg.message_id);
        if (msgIndex <= currentIndex) return false;
      }
      
      return true;
    });

    // Speak new messages
    for (const message of newAssistantMessages) {
      let textToSpeak = '';

      // Extract text from message content
      try {
        if (typeof message.content === 'string') {
          const parsed = JSON.parse(message.content);
          textToSpeak = parsed.content || parsed.text || message.content;
        } else if (message.content && typeof message.content === 'object') {
          const content = message.content as any;
          textToSpeak = content.content || content.text || JSON.stringify(content);
        }
      } catch {
        // If parsing fails, use content as-is
        textToSpeak = typeof message.content === 'string' ? message.content : '';
      }

      // Clean up text (remove markdown, XML tags, etc.)
      textToSpeak = cleanTextForSpeech(textToSpeak);

      if (textToSpeak && textToSpeak.trim().length > 0) {
        speak(textToSpeak);
        
        // Update last spoken message
        if (message.message_id) {
          lastSpokenMessageId.current = message.message_id;
        }
      }
    }
  }, [messages, ttsEnabled, isSupported, speak]);

  // Toggle TTS
  const handleToggleTTS = () => {
    if (ttsEnabled && isSpeaking) {
      stop();
    }
    setTtsEnabled(!ttsEnabled);
  };

  // Pause/resume while speaking
  const handlePauseResume = () => {
    if (isSpeaking) {
      if (window.speechSynthesis.paused) {
        resume();
      } else {
        pause();
      }
    }
  };

  // Don't render if not supported
  if (!isSupported) {
    return null;
  }

  return (
    <TooltipProvider>
      <div className={className}>
        <div className="flex items-center gap-2">
          {/* Main TTS Toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                onClick={handleToggleTTS}
                variant={ttsEnabled ? 'default' : 'outline'}
                size="sm"
                className="gap-2"
              >
                {ttsEnabled ? (
                  <>
                    <Volume2 className="h-4 w-4" />
                    Voice On
                  </>
                ) : (
                  <>
                    <VolumeX className="h-4 w-4" />
                    Voice Off
                  </>
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p>{ttsEnabled ? 'Disable' : 'Enable'} automatic voice responses</p>
              <p className="text-xs text-muted-foreground mt-1">
                Agent responses will be spoken aloud
              </p>
            </TooltipContent>
          </Tooltip>

          {/* Pause/Resume while speaking */}
          {ttsEnabled && isSpeaking && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={handlePauseResume}
                  variant="ghost"
                  size="sm"
                >
                  {window.speechSynthesis?.paused ? (
                    <Play className="h-4 w-4" />
                  ) : (
                    <Pause className="h-4 w-4" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{window.speechSynthesis?.paused ? 'Resume' : 'Pause'} voice</p>
              </TooltipContent>
            </Tooltip>
          )}

          {/* Speaking indicator */}
          {ttsEnabled && isSpeaking && (
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <div className="flex gap-1">
                <div className="w-1 h-3 bg-primary animate-pulse" style={{ animationDelay: '0ms' }}></div>
                <div className="w-1 h-3 bg-primary animate-pulse" style={{ animationDelay: '150ms' }}></div>
                <div className="w-1 h-3 bg-primary animate-pulse" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="text-xs">Speaking...</span>
            </div>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
};

/**
 * Clean text for speech synthesis
 * Removes markdown, XML tags, code blocks, etc.
 */
function cleanTextForSpeech(text: string): string {
  if (!text) return '';

  let cleaned = text;

  // Remove XML/HTML tags
  cleaned = cleaned.replace(/<[^>]+>/g, '');

  // Remove markdown code blocks
  cleaned = cleaned.replace(/```[\s\S]*?```/g, '[code block]');
  cleaned = cleaned.replace(/`[^`]+`/g, '');

  // Remove markdown links but keep text
  cleaned = cleaned.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

  // Remove markdown formatting
  cleaned = cleaned.replace(/[*_~`]/g, '');

  // Remove URLs
  cleaned = cleaned.replace(/https?:\/\/[^\s]+/g, '');

  // Remove multiple spaces/newlines
  cleaned = cleaned.replace(/\s+/g, ' ');

  // Remove special characters that sound weird
  cleaned = cleaned.replace(/[#>]/g, '');

  return cleaned.trim();
}
