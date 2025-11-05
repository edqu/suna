'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useVoiceInput } from '@/hooks/use-voice-input';
import { cn } from '@/lib/utils';

export interface VoiceControlsProps {
  onTranscriptionComplete?: (text: string) => void;
  enabled?: boolean;
  voiceEnabled?: boolean;
  className?: string;
  compact?: boolean;
}

interface VoiceOption {
  value: string;
  label: string;
  lang: string;
}

const VOICE_OPTIONS: VoiceOption[] = [
  { value: 'en-US', label: 'English (US)', lang: 'en-US' },
  { value: 'en-GB', label: 'English (UK)', lang: 'en-GB' },
  { value: 'es-ES', label: 'Spanish', lang: 'es-ES' },
  { value: 'fr-FR', label: 'French', lang: 'fr-FR' },
  { value: 'de-DE', label: 'German', lang: 'de-DE' },
  { value: 'it-IT', label: 'Italian', lang: 'it-IT' },
  { value: 'pt-BR', label: 'Portuguese', lang: 'pt-BR' },
  { value: 'ja-JP', label: 'Japanese', lang: 'ja-JP' },
  { value: 'ko-KR', label: 'Korean', lang: 'ko-KR' },
  { value: 'zh-CN', label: 'Chinese', lang: 'zh-CN' },
];

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  onTranscriptionComplete,
  enabled = true,
  voiceEnabled = true,
  className,
  compact = false,
}) => {
  const [selectedLang, setSelectedLang] = useState('en-US');
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [showFullControls, setShowFullControls] = useState(false);

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
    lang: selectedLang,
    onTranscriptionComplete: (text) => {
      if (onTranscriptionComplete) {
        onTranscriptionComplete(text);
      }
      resetTranscript();
    },
  });

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleTtsToggle = () => {
    setTtsEnabled(!ttsEnabled);
  };

  if (!isSupported) {
    return null;
  }

  if (compact) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleMicClick}
              disabled={!enabled}
              className={cn(
                'h-8 w-8 p-0 bg-transparent border-0 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-all duration-200',
                isRecording && 'text-red-500 hover:text-red-600 animate-pulse',
                className,
              )}
            >
              {isRecording ? (
                <MicOff className="h-5 w-5" />
              ) : (
                <Mic className="h-5 w-5" />
              )}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <div className="space-y-1">
              <p className="font-medium">
                {isRecording ? 'Stop recording' : 'Start voice input'}
              </p>
              {error && <p className="text-xs text-red-400">{error}</p>}
              {(transcript || interimTranscript) && (
                <p className="text-xs text-muted-foreground max-w-[200px] truncate">
                  {transcript + interimTranscript}
                </p>
              )}
            </div>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return (
    <Card className={cn('w-full max-w-md', className)}>
      <CardContent className="p-4 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium">Voice Controls</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowFullControls(!showFullControls)}
            className="text-xs"
          >
            {showFullControls ? 'Hide' : 'Show'} Options
          </Button>
        </div>

        {showFullControls && (
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-2">
              <label className="text-xs text-muted-foreground">Language</label>
              <Select
                value={selectedLang}
                onValueChange={setSelectedLang}
                disabled={isRecording}
              >
                <SelectTrigger className="w-[180px] h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {VOICE_OPTIONS.map((option) => (
                    <SelectItem
                      key={option.value}
                      value={option.value}
                      className="text-xs"
                    >
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <label className="text-xs text-muted-foreground">
                Text-to-Speech
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleTtsToggle}
                className="h-8 w-8 p-0"
              >
                {ttsEnabled ? (
                  <Volume2 className="h-4 w-4 text-green-500" />
                ) : (
                  <VolumeX className="h-4 w-4 text-muted-foreground" />
                )}
              </Button>
            </div>
          </div>
        )}

        <div className="flex items-center justify-center gap-4">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="default"
                  size="lg"
                  onClick={handleMicClick}
                  disabled={!enabled}
                  className={cn(
                    'h-16 w-16 rounded-full transition-all duration-200',
                    isRecording &&
                      'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-500/50',
                  )}
                >
                  {isRecording ? (
                    <MicOff className="h-8 w-8" />
                  ) : (
                    <Mic className="h-8 w-8" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{isRecording ? 'Stop recording' : 'Start recording'}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>

        {(transcript || interimTranscript || error) && (
          <div className="space-y-2">
            {error && (
              <div className="p-2 rounded-lg bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900">
                <p className="text-xs text-red-600 dark:text-red-400">
                  {error}
                </p>
              </div>
            )}

            {(transcript || interimTranscript) && (
              <div className="p-3 rounded-lg bg-muted/50 border border-border">
                <p className="text-xs text-muted-foreground mb-1">Transcript</p>
                <p className="text-sm">
                  {transcript}
                  {interimTranscript && (
                    <span className="text-muted-foreground italic">
                      {interimTranscript}
                    </span>
                  )}
                </p>
              </div>
            )}
          </div>
        )}

        {isRecording && (
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <div className="flex gap-1">
              <div
                className="w-1 h-3 bg-red-500 rounded-full animate-pulse"
                style={{ animationDelay: '0ms' }}
              />
              <div
                className="w-1 h-3 bg-red-500 rounded-full animate-pulse"
                style={{ animationDelay: '150ms' }}
              />
              <div
                className="w-1 h-3 bg-red-500 rounded-full animate-pulse"
                style={{ animationDelay: '300ms' }}
              />
            </div>
            <span>Listening...</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
