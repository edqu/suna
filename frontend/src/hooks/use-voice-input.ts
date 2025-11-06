'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message?: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onresult:
    | ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any)
    | null;
  onerror:
    | ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any)
    | null;
}

declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

export interface UseVoiceInputOptions {
  continuous?: boolean;
  interimResults?: boolean;
  lang?: string;
  onTranscriptionComplete?: (transcript: string) => void;
}

export interface UseVoiceInputReturn {
  isRecording: boolean;
  transcript: string;
  interimTranscript: string;
  error: string | null;
  isSupported: boolean;
  startRecording: () => void;
  stopRecording: () => void;
  resetTranscript: () => void;
}

export const useVoiceInput = (
  options: UseVoiceInputOptions = {},
): UseVoiceInputReturn => {
  const {
    continuous = false,
    interimResults = true,
    lang = 'en-US',
    onTranscriptionComplete,
  } = options;

  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState(false);

  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      setIsSupported(!!SpeechRecognition);

      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
      }
    }

    return () => {
      if (recognitionRef.current && isRecording) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startRecording = useCallback(() => {
    if (!recognitionRef.current) {
      setError('Speech recognition not supported in this browser');
      return;
    }

    setError(null);
    setTranscript('');
    setInterimTranscript('');

    const recognition = recognitionRef.current;
    recognition.continuous = continuous;
    recognition.interimResults = interimResults;
    recognition.lang = lang;

    recognition.onstart = () => {
      setIsRecording(true);
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcriptPart = result[0].transcript;

        if (result.isFinal) {
          final += transcriptPart + ' ';
        } else {
          interim += transcriptPart;
        }
      }

      if (final) {
        setTranscript((prev) => prev + final);
      }
      setInterimTranscript(interim);
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);

      let errorMessage = 'An error occurred';
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'No microphone found or permission denied.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone permission denied.';
          break;
        case 'network':
          errorMessage = 'Network error occurred.';
          break;
        case 'aborted':
          errorMessage = 'Recording aborted.';
          break;
        default:
          errorMessage = event.message || `Error: ${event.error}`;
      }

      setError(errorMessage);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
      const finalTranscript = transcript;
      if (finalTranscript.trim() && onTranscriptionComplete) {
        onTranscriptionComplete(finalTranscript.trim());
      }
    };

    try {
      recognition.start();
    } catch (err) {
      console.error('Error starting recognition:', err);
      setError('Failed to start recording');
      setIsRecording(false);
    }
  }, [continuous, interimResults, lang, onTranscriptionComplete, transcript]);

  const stopRecording = useCallback(() => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
    }
  }, [isRecording]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  return {
    isRecording,
    transcript,
    interimTranscript,
    error,
    isSupported,
    startRecording,
    stopRecording,
    resetTranscript,
  };
};
