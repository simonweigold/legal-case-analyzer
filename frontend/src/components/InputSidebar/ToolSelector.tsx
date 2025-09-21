// components/InputSidebar/ToolSelector.tsx
import React, { useState, useEffect } from 'react';
import { Check, X, Wrench, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';

export interface Tool {
  name: string;
  description: string;
  category: string;
  streaming: boolean;
  parameters: Array<{
    name: string;
    type: string;
    description: string;
    required: boolean;
    default?: any;
  }>;
}

export interface ToolSelectorProps {
  selectedTools: string[];
  onToolsChange: (tools: string[]) => void;
  className?: string;
}

export function ToolSelector({ selectedTools, onToolsChange, className = "" }: ToolSelectorProps) {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  // Fetch available tools from backend
  useEffect(() => {
    const fetchTools = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/tools');
        if (!response.ok) {
          throw new Error('Failed to fetch tools');
        }
        const toolsData = await response.json();
        setTools(toolsData);
        
        // If no tools are selected, select all by default
        if (selectedTools.length === 0) {
          onToolsChange(toolsData.map((tool: Tool) => tool.name));
        }
      } catch (err) {
        console.error('Error fetching tools:', err);
        setError(err instanceof Error ? err.message : 'Failed to load tools');
      } finally {
        setLoading(false);
      }
    };

    fetchTools();
  }, []);

  const toggleTool = (toolName: string) => {
    if (selectedTools.includes(toolName)) {
      onToolsChange(selectedTools.filter(t => t !== toolName));
    } else {
      onToolsChange([...selectedTools, toolName]);
    }
  };

  const selectAll = () => {
    onToolsChange(tools.map(tool => tool.name));
  };

  const deselectAll = () => {
    onToolsChange([]);
  };

  if (loading) {
    return (
      <div className={`p-4 border rounded-lg bg-white ${className}`}>
        <div className="flex items-center gap-2 mb-3">
          <Wrench className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Analysis Tools</span>
          <Loader2 className="w-4 h-4 animate-spin ml-auto" />
        </div>
        <div className="text-xs text-muted-foreground">Loading available tools...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 border rounded-lg bg-white ${className}`}>
        <div className="flex items-center gap-2 mb-3">
          <Wrench className="w-4 h-4 text-red-500" />
          <span className="text-sm font-medium text-red-500">Tools Error</span>
        </div>
        <div className="text-xs text-red-500">{error}</div>
      </div>
    );
  }

  const regularTools = tools.filter(tool => !tool.streaming);
  const streamingTools = tools.filter(tool => tool.streaming);
  const selectedCount = selectedTools.length;
  const totalCount = tools.length;

  return (
    <div className={`p-4 border rounded-lg bg-white ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Wrench className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">Analysis Tools</span>
          <span className="text-xs text-muted-foreground">
            ({selectedCount}/{totalCount} selected)
          </span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setExpanded(!expanded)}
          className="text-xs px-2 py-1 h-auto"
        >
          {expanded ? 'Hide' : 'Show'}
        </Button>
      </div>

      {expanded && (
        <>
          <div className="flex gap-2 mb-3">
            <Button
              variant="outline"
              size="sm"
              onClick={selectAll}
              className="text-xs px-2 py-1 h-auto flex-1"
            >
              <Check className="w-3 h-3 mr-1" />
              All
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={deselectAll}
              className="text-xs px-2 py-1 h-auto flex-1"
            >
              <X className="w-3 h-3 mr-1" />
              None
            </Button>
          </div>

          <div className="space-y-3 max-h-48 overflow-y-auto">
            {regularTools.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-2">
                  Standard Tools
                </h4>
                <div className="space-y-1">
                  {regularTools.map((tool) => (
                    <label
                      key={tool.name}
                      className="flex items-start gap-2 cursor-pointer p-2 hover:bg-muted/30 rounded text-xs group"
                    >
                      <input
                        type="checkbox"
                        checked={selectedTools.includes(tool.name)}
                        onChange={() => toggleTool(tool.name)}
                        className="mt-0.5 rounded"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate group-hover:text-primary">
                          {tool.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </div>
                        <div className="text-muted-foreground mt-1 line-clamp-2">
                          {tool.description}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {streamingTools.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-muted-foreground mb-2">
                  Streaming Tools
                </h4>
                <div className="space-y-1">
                  {streamingTools.map((tool) => (
                    <label
                      key={tool.name}
                      className="flex items-start gap-2 cursor-pointer p-2 hover:bg-muted/30 rounded text-xs group"
                    >
                      <input
                        type="checkbox"
                        checked={selectedTools.includes(tool.name)}
                        onChange={() => toggleTool(tool.name)}
                        className="mt-0.5 rounded"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium truncate group-hover:text-primary">
                          {tool.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          <span className="ml-1 text-blue-500 text-xs">⚡</span>
                        </div>
                        <div className="text-muted-foreground mt-1 line-clamp-2">
                          {tool.description}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>

          {selectedCount === 0 && (
            <div className="text-xs text-amber-600 mt-3 p-2 bg-amber-50 rounded">
              ⚠️ No tools selected. The AI will only use general knowledge.
            </div>
          )}
        </>
      )}

      {!expanded && selectedCount > 0 && (
        <div className="text-xs text-muted-foreground">
          {selectedCount === totalCount 
            ? "All tools selected" 
            : `${selectedTools.slice(0, 3).map(name => name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())).join(', ')}${selectedCount > 3 ? ` and ${selectedCount - 3} more` : ''}`}
        </div>
      )}
    </div>
  );
}
