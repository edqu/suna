'use client';

import React, { useState } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { useVoiceInput } from '@/hooks/use-voice-input';
import { cn } from '@/lib/utils';

export interface EnhancedVoiceRecorderProps {
  onTranscription: (text: string) => void;
  disabled?: boolean;
  lang?: string;
  className?: string;
}

export const EnhancedVoiceRecorder: React.FC<EnhancedVoiceRecorderProps> = ({
  onTranscription,
  disabled = false,
  lang = 'en-US',
  className,
}) => {
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
    lang,
    onTranscriptionComplete: (text) => {
      onTranscription(text);
      resetTranscript();
    },
  });

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  if (!isSupported) {
    return null;
  }

  const displayTranscript = transcript + interimTranscript;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleClick}
            disabled={disabled}
            className={cn(
              'h-8 px-2 py-2 bg-transparent border-0 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent/50 transition-all duration-200 relative',
              isRecording && 'text-red-500 hover:text-red-600',
              className,
            )}
          >
            {isRecording ? (
              <>
                <MicOff className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                </span>
              </>
            ) : (
              <Mic className="h-5 w-5" />
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent side="top" className="max-w-[300px]">
          <div className="space-y-1">
            <p className="font-medium">
              {isRecording ? 'Click to stop recording' : 'Record voice message'}
            </p>
            <p className="text-xs text-muted-foreground">
              Free browser-based speech recognition
            </p>
            {error && <p className="text-xs text-red-400 mt-1">{error}</p>}
            {displayTranscript && (
              <div className="mt-2 p-2 bg-muted/50 rounded text-xs max-h-20 overflow-y-auto">
                {transcript && <span>{transcript}</span>}
                {interimTranscript && (
                  <span className="text-muted-foreground italic">
                    {interimTranscript}
                  </span>
                )}
              </div>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};
