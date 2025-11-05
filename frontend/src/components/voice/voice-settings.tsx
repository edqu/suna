'use client';

import React, { useState, useEffect } from 'react';
import { Volume2, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';

interface VoiceSettingsProps {
  onVoiceChange?: (voiceName: string) => void;
  onRateChange?: (rate: number) => void;
  className?: string;
  compact?: boolean;
}

interface VoiceOption {
  name: string;
  lang: string;
  gender: 'female' | 'male' | 'unknown';
  isLocal: boolean;
}

export const VoiceSettings: React.FC<VoiceSettingsProps> = ({
  onVoiceChange,
  onRateChange,
  className,
  compact = false,
}) => {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>('');
  const [rate, setRate] = useState<number>(1.1);
  const [isLoading, setIsLoading] = useState(true);

  // Load voices from browser
  useEffect(() => {
    const loadVoices = () => {
      const availableVoices = window.speechSynthesis?.getVoices() || [];
      if (availableVoices.length > 0) {
        setVoices(availableVoices);
        setIsLoading(false);

        // Load saved voice preference
        const savedVoice = localStorage.getItem('selectedVoiceName');
        if (savedVoice) {
          setSelectedVoice(savedVoice);
        } else {
          // Default to first English voice
          const englishVoice = availableVoices.find(v => v.lang.startsWith('en-'));
          if (englishVoice) {
            setSelectedVoice(englishVoice.name);
          }
        }

        // Load saved rate
        const savedRate = localStorage.getItem('voiceRate');
        if (savedRate) {
          setRate(parseFloat(savedRate));
        }
      }
    };

    // Load voices
    loadVoices();

    // Some browsers need this event
    if (window.speechSynthesis) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, []);

  // Group voices by language
  const groupedVoices = React.useMemo(() => {
    const groups: Record<string, VoiceOption[]> = {};

    voices.forEach((voice) => {
      const langCode = voice.lang.split('-')[0]; // Get language code (e.g., 'en' from 'en-US')
      const langName = getLanguageName(voice.lang);

      if (!groups[langName]) {
        groups[langName] = [];
      }

      // Determine gender from voice name (heuristic)
      let gender: 'female' | 'male' | 'unknown' = 'unknown';
      const lowerName = voice.name.toLowerCase();
      const femaleKeywords = ['female', 'woman', 'girl', 'aria', 'samantha', 'victoria', 'karen', 'emily', 'jenny', 'natasha'];
      const maleKeywords = ['male', 'man', 'boy', 'alex', 'daniel', 'thomas', 'ryan', 'guy'];
      
      if (femaleKeywords.some(keyword => lowerName.includes(keyword))) {
        gender = 'female';
      } else if (maleKeywords.some(keyword => lowerName.includes(keyword))) {
        gender = 'male';
      }

      groups[langName].push({
        name: voice.name,
        lang: voice.lang,
        gender,
        isLocal: voice.localService,
      });
    });

    return groups;
  }, [voices]);

  const handleVoiceSelect = (voiceName: string) => {
    setSelectedVoice(voiceName);
    localStorage.setItem('selectedVoiceName', voiceName);
    
    if (onVoiceChange) {
      onVoiceChange(voiceName);
    }

    // Trigger event for other components
    window.dispatchEvent(new CustomEvent('voiceSettingsChanged', { 
      detail: { voice: voiceName, rate } 
    }));
  };

  const handleRateChange = (newRate: number[]) => {
    const rateValue = newRate[0];
    setRate(rateValue);
    localStorage.setItem('voiceRate', String(rateValue));
    
    if (onRateChange) {
      onRateChange(rateValue);
    }

    window.dispatchEvent(new CustomEvent('voiceSettingsChanged', { 
      detail: { voice: selectedVoice, rate: rateValue } 
    }));
  };

  const selectedVoiceObj = voices.find(v => v.name === selectedVoice);

  if (compact) {
    // Compact version - just dropdown
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className={className}>
            <Volume2 className="h-4 w-4 mr-2" />
            {selectedVoiceObj ? getShortVoiceName(selectedVoiceObj.name) : 'Voice'}
            <ChevronDown className="h-3 w-3 ml-1" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-64 max-h-96 overflow-y-auto">
          <DropdownMenuLabel>Select Voice</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {Object.entries(groupedVoices).map(([language, voiceOptions]) => (
            <React.Fragment key={language}>
              <DropdownMenuLabel className="text-xs text-muted-foreground px-2 py-1">
                {language}
              </DropdownMenuLabel>
              {voiceOptions.slice(0, 5).map((voice) => (
                <DropdownMenuItem
                  key={voice.name}
                  onClick={() => handleVoiceSelect(voice.name)}
                  className="flex items-center justify-between"
                >
                  <span className="flex-1">
                    {getShortVoiceName(voice.name)}
                    {voice.gender !== 'unknown' && (
                      <span className="text-xs text-muted-foreground ml-2">
                        ({voice.gender})
                      </span>
                    )}
                  </span>
                  {selectedVoice === voice.name && (
                    <span className="text-primary">✓</span>
                  )}
                </DropdownMenuItem>
              ))}
            </React.Fragment>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  // Full version with rate slider
  return (
    <div className={className}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <Volume2 className="h-4 w-4 mr-2" />
            {selectedVoiceObj ? (
              <span>
                {getShortVoiceName(selectedVoiceObj.name)}
                <span className="text-xs text-muted-foreground ml-2">
                  {selectedVoiceObj.lang}
                </span>
              </span>
            ) : (
              'Select Voice'
            )}
            <ChevronDown className="h-3 w-3 ml-2" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-80 max-h-96 overflow-y-auto">
          <DropdownMenuLabel>Voice Settings</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {/* Speed/Rate Slider */}
          <div className="px-3 py-2 space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs">Speech Rate</Label>
              <span className="text-xs text-muted-foreground">{rate.toFixed(1)}x</span>
            </div>
            <Slider
              value={[rate]}
              onValueChange={handleRateChange}
              min={0.5}
              max={2.0}
              step={0.1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Slow</span>
              <span>Normal</span>
              <span>Fast</span>
            </div>
          </div>
          
          <DropdownMenuSeparator />
          <DropdownMenuLabel>Select Voice</DropdownMenuLabel>
          
          {isLoading ? (
            <div className="px-3 py-2 text-sm text-muted-foreground">
              Loading voices...
            </div>
          ) : (
            Object.entries(groupedVoices).map(([language, voiceOptions]) => (
              <React.Fragment key={language}>
                <DropdownMenuLabel className="text-xs text-muted-foreground px-2 py-1 bg-muted/50">
                  {language}
                </DropdownMenuLabel>
                {voiceOptions.map((voice) => (
                  <DropdownMenuItem
                    key={voice.name}
                    onClick={() => handleVoiceSelect(voice.name)}
                    className="flex items-center justify-between px-3"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">
                          {getShortVoiceName(voice.name)}
                        </span>
                        {voice.gender !== 'unknown' && (
                          <span className="text-xs px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                            {voice.gender === 'female' ? '♀' : '♂'}
                          </span>
                        )}
                        {!voice.isLocal && (
                          <span className="text-xs px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                            Cloud
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {voice.lang}
                      </div>
                    </div>
                    {selectedVoice === voice.name && (
                      <span className="text-primary font-semibold">✓</span>
                    )}
                  </DropdownMenuItem>
                ))}
              </React.Fragment>
            ))
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
};

// Helper function to get short voice name (remove system-specific prefixes)
function getShortVoiceName(fullName: string): string {
  // Remove common prefixes
  let name = fullName
    .replace('Microsoft ', '')
    .replace('Google ', '')
    .replace('Apple ', '')
    .replace('Samantha', 'Samantha')
    .replace('Alex', 'Alex');

  // If still long, try to extract just the first part
  if (name.length > 25) {
    const parts = name.split(' ');
    name = parts[0];
  }

  return name;
}

// Helper function to get language name from code
function getLanguageName(langCode: string): string {
  const languageNames: Record<string, string> = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'pl': 'Polish',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
  };

  const code = langCode.split('-')[0];
  return languageNames[code] || langCode;
}
