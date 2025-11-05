'use client';

import React, { useState, useEffect } from 'react';
import { Globe, Zap, DollarSign, Check, Search, FileText } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { updateWebSearchPreference } from '@/lib/api';
import { cn } from '@/lib/utils';

interface WebSearchPreferenceToggleProps {
  agentId: string;
  currentPreference?: 'local' | 'paid';
  onPreferenceChange?: (newPreference: 'local' | 'paid') => void;
}

export function WebSearchPreferenceToggle({
  agentId,
  currentPreference = 'local',
  onPreferenceChange,
}: WebSearchPreferenceToggleProps) {
  const [preference, setPreference] = useState<'local' | 'paid'>(
    currentPreference,
  );
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setPreference(currentPreference);
  }, [currentPreference]);

  const handleToggle = async (checked: boolean) => {
    const newPreference = checked ? 'paid' : 'local';

    setIsLoading(true);

    try {
      const response = await updateWebSearchPreference(agentId, newPreference);

      if (response.success) {
        setPreference(newPreference);

        toast.success('Web search mode updated', {
          description:
            newPreference === 'local'
              ? 'Now using free DuckDuckGo search and BeautifulSoup scraping'
              : 'Now using Tavily search and Firecrawl scraping (API keys required)',
        });

        onPreferenceChange?.(newPreference);
      } else {
        throw new Error(response.message || 'Failed to update preference');
      }
    } catch (error) {
      console.error('Error updating web search preference:', error);

      toast.error('Failed to update preference', {
        description:
          error instanceof Error ? error.message : 'Please try again',
      });

      // Revert to previous state
      setPreference(preference);
    } finally {
      setIsLoading(false);
    }
  };

  const isPaid = preference === 'paid';

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Globe className="h-5 w-5 text-muted-foreground" />
            <CardTitle>Web Search Mode</CardTitle>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant={isPaid ? 'outline' : 'highlight'}>
              {isPaid ? 'PAID' : 'FREE'}
            </Badge>
            <Switch
              checked={isPaid}
              onCheckedChange={handleToggle}
              disabled={isLoading}
            />
          </div>
        </div>
        <CardDescription>
          Choose between free local tools or premium API services for web search
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Local/Free Option */}
          <div
            className={cn(
              'relative rounded-lg border p-4 transition-all',
              !isPaid
                ? 'border-green-500 bg-green-50 dark:bg-green-950/20'
                : 'border-gray-200 dark:border-gray-800 opacity-60',
            )}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-green-600 dark:text-green-400" />
                <h3 className="font-semibold text-sm">Local & Free</h3>
              </div>
              {!isPaid && (
                <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
              )}
            </div>

            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex items-start gap-2">
                <Search className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                <div>
                  <span className="font-medium text-foreground">
                    DuckDuckGo
                  </span>
                  <p>Privacy-focused search engine</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <FileText className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                <div>
                  <span className="font-medium text-foreground">
                    BeautifulSoup
                  </span>
                  <p>Web scraping and parsing</p>
                </div>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t">
              <div className="flex items-center gap-1.5 text-xs font-medium text-green-600 dark:text-green-400">
                <DollarSign className="h-3.5 w-3.5" />
                <span>No API keys required</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Free to use, no additional costs
              </p>
            </div>
          </div>

          {/* Paid Option */}
          <div
            className={cn(
              'relative rounded-lg border p-4 transition-all',
              isPaid
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                : 'border-gray-200 dark:border-gray-800 opacity-60',
            )}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <h3 className="font-semibold text-sm">Premium APIs</h3>
              </div>
              {isPaid && (
                <Check className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              )}
            </div>

            <div className="space-y-2 text-xs text-muted-foreground">
              <div className="flex items-start gap-2">
                <Search className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                <div>
                  <span className="font-medium text-foreground">Tavily</span>
                  <p>AI-optimized search API</p>
                </div>
              </div>
              <div className="flex items-start gap-2">
                <FileText className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                <div>
                  <span className="font-medium text-foreground">Firecrawl</span>
                  <p>Advanced web scraping API</p>
                </div>
              </div>
            </div>

            <div className="mt-3 pt-3 border-t">
              <div className="flex items-center gap-1.5 text-xs font-medium text-blue-600 dark:text-blue-400">
                <Zap className="h-3.5 w-3.5" />
                <span>API keys required</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Pay-per-use pricing from providers
              </p>
            </div>
          </div>
        </div>

        {/* Cost Information */}
        <div className="mt-4 p-3 rounded-lg bg-muted/50 text-xs text-muted-foreground">
          <p className="font-medium text-foreground mb-1">
            💡 Cost Information
          </p>
          <ul className="space-y-1 list-disc list-inside">
            <li>
              <span className="font-medium">Local/Free:</span> No costs,
              unlimited usage
            </li>
            <li>
              <span className="font-medium">Tavily:</span> ~$0.005 per search
              request
            </li>
            <li>
              <span className="font-medium">Firecrawl:</span> ~$0.01 per page
              scraped
            </li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
