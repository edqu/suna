'use client';

import React, { useEffect, useMemo, useState } from 'react';
import dynamic from 'next/dynamic';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronDown, Cpu, Check, AlertCircle, Download, CheckCircle } from 'lucide-react';
import { useModelSelection } from '@/hooks/use-model-selection';
import { cn } from '@/lib/utils';

interface SimpleModelSelectorProps {
  value?: string;
  onChange: (model: string) => void;
  disabled?: boolean;
  className?: string;
}

export function SimpleModelSelector({
  value,
  onChange,
  disabled = false,
  className,
}: SimpleModelSelectorProps) {
  const {
    availableModels,
    selectedModel: storeSelectedModel,
    isLoading,
  } = useModelSelection();

  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Determine a safe selected value - don't auto-select first model
  const safeSelectedModel = useMemo(() => {
    return value || storeSelectedModel || null;
  }, [value, storeSelectedModel]);

  const selectedLabel = useMemo(() => {
    if (!safeSelectedModel) return 'Select a model';
    const m = availableModels.find(m => m.id === safeSelectedModel);
    return m?.label || safeSelectedModel;
  }, [safeSelectedModel, availableModels]);

  // Only auto-initialize if user has a stored preference
  useEffect(() => {
    if (!value && storeSelectedModel && !isLoading) {
      onChange(storeSelectedModel);
    }
  }, [value, storeSelectedModel, onChange, isLoading]);

  const handleSelect = (id: string) => {
    onChange(id);
    setOpen(false);
  };

  // Show loading state during mount to prevent hydration mismatch
  if (!mounted || isLoading) {
    return (
      <Button
        variant="outline"
        size="sm"
        disabled={true}
        className={cn("justify-between", className)}
      >
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4" />
          <span className="text-sm">Loading models...</span>
        </div>
      </Button>
    );
  }

  if (availableModels.length === 0) {
    return (
      <Button
        variant="outline"
        size="sm"
        disabled={true}
        className={cn("justify-between", className)}
      >
        <div className="flex items-center gap-2">
          <Cpu className="h-4 w-4" />
          <span className="text-sm text-muted-foreground">No models available</span>
        </div>
      </Button>
    );
  }

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          disabled={disabled}
          className={cn("justify-between min-w-[240px]", className)}
        >
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4" />
            <span className="text-sm truncate">{selectedLabel}</span>
          </div>
          <ChevronDown className="h-4 w-4 opacity-50 ml-2 flex-shrink-0" />
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="start" className="w-[280px]">
        <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
          Available Models
        </div>
        {availableModels.map((model) => {
          // @ts-ignore - status might not be in type yet
          const status = model.status || 'remote';
          const isInstalled = status === 'installed';
          const isServerDown = status === 'server_down';
          const isNotInstalled = status === 'not_installed';
          
          return (
            <DropdownMenuItem
              key={model.id}
              onClick={() => handleSelect(model.id)}
              className={cn(
                "cursor-pointer flex items-center justify-between",
                isNotInstalled && "opacity-60"
              )}
            >
              <div className="flex flex-col gap-1 flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="truncate font-medium">{model.label}</span>
                  {isInstalled && (
                    <CheckCircle className="h-3 w-3 text-green-500 flex-shrink-0" />
                  )}
                  {isServerDown && (
                    <AlertCircle className="h-3 w-3 text-red-500 flex-shrink-0" />
                  )}
                  {isNotInstalled && (
                    <Download className="h-3 w-3 text-yellow-500 flex-shrink-0" />
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {model.contextWindow && (
                    <span>{(model.contextWindow / 1000).toFixed(0)}K context</span>
                  )}
                  {!model.requiresSubscription && status === 'installed' && (
                    <span className="text-green-600 dark:text-green-400">• Free (Local)</span>
                  )}
                  {isNotInstalled && (
                    <span className="text-yellow-600 dark:text-yellow-400">• Not installed</span>
                  )}
                  {isServerDown && (
                    <span className="text-red-600 dark:text-red-400">• Ollama offline</span>
                  )}
                </div>
              </div>
              {safeSelectedModel === model.id && (
                <Check className="h-4 w-4 text-primary flex-shrink-0" />
              )}
            </DropdownMenuItem>
          );
        })}
        
        {availableModels.some(m => m.requiresSubscription === false) && (
          <div className="px-2 py-1.5 mt-1 border-t">
            <div className="text-xs text-muted-foreground">
              💡 Free local models via Ollama
            </div>
          </div>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
