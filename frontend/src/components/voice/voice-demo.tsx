'use client';

import React, { useState } from 'react';
import { VoiceControls } from './voice-controls';
import { EnhancedVoiceRecorder } from './enhanced-voice-recorder';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export const VoiceDemo: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);

  const handleTranscription = (text: string) => {
    setMessages((prev) => [...prev, text]);
  };

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-4xl">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Voice Interface Demo</h1>
        <p className="text-muted-foreground">
          Free browser-based speech recognition for Suna
        </p>
        <div className="flex gap-2">
          <Badge variant="secondary">Web Speech API</Badge>
          <Badge variant="outline">Zero Cost</Badge>
          <Badge variant="outline">No Server Required</Badge>
        </div>
      </div>

      <Tabs defaultValue="compact" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="compact">Compact Mode</TabsTrigger>
          <TabsTrigger value="full">Full Controls</TabsTrigger>
        </TabsList>

        <TabsContent value="compact" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compact Voice Recorder</CardTitle>
              <CardDescription>
                Minimal UI for inline integration in chat interfaces
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-center p-8 bg-muted/50 rounded-lg">
                <EnhancedVoiceRecorder
                  onTranscription={handleTranscription}
                  lang="en-US"
                />
              </div>
              
              <div className="space-y-2">
                <h3 className="text-sm font-medium">Features</h3>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li>One-click recording</li>
                  <li>Visual recording indicator</li>
                  <li>Real-time transcript preview in tooltip</li>
                  <li>Error handling</li>
                  <li>Auto-complete on stop</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="full" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Full Voice Controls</CardTitle>
              <CardDescription>
                Complete voice interface with language selection and settings
              </CardDescription>
            </CardHeader>
            <CardContent>
              <VoiceControls
                onTranscriptionComplete={handleTranscription}
                enabled={true}
                compact={false}
                className="mx-auto"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Transcription History</CardTitle>
          <CardDescription>
            Messages transcribed during this session
          </CardDescription>
        </CardHeader>
        <CardContent>
          {messages.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No messages yet. Try recording something!
            </p>
          ) : (
            <div className="space-y-3">
              {messages.map((message, index) => (
                <div key={index} className="p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm flex-1">{message}</p>
                    <Badge variant="outline" className="text-xs">
                      #{index + 1}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Integration Example</CardTitle>
          <CardDescription>
            How to integrate into your chat input
          </CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="text-xs bg-muted p-4 rounded-lg overflow-x-auto">
{`import { EnhancedVoiceRecorder } from '@/components/voice';

function ChatInput() {
  const handleTranscription = (text: string) => {
    // Insert text into input
    setInputValue(prev => prev + ' ' + text);
  };

  return (
    <div className="flex items-center gap-2">
      <input 
        value={inputValue} 
        onChange={...}
      />
      <EnhancedVoiceRecorder
        onTranscription={handleTranscription}
        lang="en-US"
      />
      <button type="submit">Send</button>
    </div>
  );
}`}
          </pre>
        </CardContent>
      </Card>

      <Card className="border-blue-200 dark:border-blue-900">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-blue-600 dark:text-blue-400">💡</span>
            Browser Support
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="grid grid-cols-2 gap-2">
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Chrome/Edge</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-green-500">✓</span>
              <span>Safari 14.1+</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-yellow-500">⚠</span>
              <span>Firefox (limited)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-red-500">✗</span>
              <span>Internet Explorer</span>
            </div>
          </div>
          <Separator className="my-2" />
          <p className="text-xs text-muted-foreground">
            The components automatically detect browser support and hide if unavailable.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
