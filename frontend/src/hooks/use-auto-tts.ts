'use client';

import { useEffect, useRef, useState } from 'react';

export interface AutoTTSOptions {
  enabled: boolean;
  voice?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
  lang?: string;
}

export const useAutoTTS = (options: AutoTTSOptions) => {
  const {
    enabled = false,
    voice,
    rate = 1.0,
    pitch = 1.0,
    volume = 1.0,
    lang = 'en-US',
  } = options;

  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [isActivated, setIsActivated] = useState(false);  // User must activate TTS first
  const [currentVoice, setCurrentVoice] = useState<string | undefined>(voice);
  const [currentRate, setCurrentRate] = useState(rate);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const queueRef = useRef<string[]>([]);

  // Check if browser supports TTS
  useEffect(() => {
    setIsSupported('speechSynthesis' in window);
  }, []);

  // Listen for voice settings changes from VoiceSettings component
  useEffect(() => {
    const handleSettingsChange = (event: CustomEvent) => {
      const { voice: newVoice, rate: newRate } = event.detail;
      if (newVoice) setCurrentVoice(newVoice);
      if (newRate) setCurrentRate(newRate);
    };

    window.addEventListener('voiceSettingsChanged', handleSettingsChange as EventListener);
    return () => window.removeEventListener('voiceSettingsChanged', handleSettingsChange as EventListener);
  }, []);

  // Load saved preferences on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedVoice = localStorage.getItem('selectedVoiceName');
      const savedRate = localStorage.getItem('voiceRate');
      
      if (savedVoice) setCurrentVoice(savedVoice);
      if (savedRate) setCurrentRate(parseFloat(savedRate));
    }
  }, []);

  // Activate TTS (required on first use due to browser autoplay policy)
  const activate = () => {
    if (!isSupported) return;
    
    // Speak a silent utterance to activate TTS
    const silentUtterance = new SpeechSynthesisUtterance('');
    silentUtterance.volume = 0;
    window.speechSynthesis.speak(silentUtterance);
    setIsActivated(true);
    
    // Save activation state
    if (typeof window !== 'undefined') {
      localStorage.setItem('ttsActivated', 'true');
    }
  };

  // Check if already activated
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const wasActivated = localStorage.getItem('ttsActivated') === 'true';
      setIsActivated(wasActivated);
    }
  }, []);

  // Speak text using Web Speech API
  const speak = (text: string) => {
    if (!isSupported || !enabled || !text.trim()) {
      return;
    }

    // Auto-activate if not activated yet (user has interacted by enabling voice)
    if (!isActivated && enabled) {
      activate();
    }

    // Cancel any ongoing speech
    if (window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = currentRate; // Use current rate from state
    utterance.pitch = pitch;
    utterance.volume = volume;

    // Set voice - use currentVoice from state or fallback to prop
    const voiceToUse = currentVoice || voice;
    if (voiceToUse) {
      const voices = window.speechSynthesis.getVoices();
      const selectedVoice = voices.find(v => v.name === voiceToUse || v.lang === voiceToUse);
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      // Speak next in queue if any
      if (queueRef.current.length > 0) {
        const nextText = queueRef.current.shift();
        if (nextText) {
          speak(nextText);
        }
      }
    };

    utterance.onerror = (event: SpeechSynthesisErrorEvent) => {
      // Suppress "not-allowed" errors completely (browser autoplay policy)
      if (event.error !== 'not-allowed') {
        console.error('TTS error:', event.error);
      }
      setIsSpeaking(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  // Stop speaking
  const stop = () => {
    if (isSupported && window.speechSynthesis.speaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      queueRef.current = [];
    }
  };

  // Pause speaking
  const pause = () => {
    if (isSupported && window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
    }
  };

  // Resume speaking
  const resume = () => {
    if (isSupported && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
  };

  // Add to queue
  const queueText = (text: string) => {
    if (!enabled || !isSupported) return;
    
    if (isSpeaking) {
      queueRef.current.push(text);
    } else {
      speak(text);
    }
  };

  // Get available voices
  const getVoices = (): SpeechSynthesisVoice[] => {
    if (!isSupported) return [];
    return window.speechSynthesis.getVoices();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (isSupported && window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
      }
    };
  }, [isSupported]);

  return {
    speak,
    stop,
    pause,
    resume,
    queueText,
    getVoices,
    activate,
    isSpeaking,
    isSupported,
    isActivated,
    isEnabled: enabled && isSupported,
  };
};
