'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getModels, chatCompletion } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { MessageSquare, Send, Trash2, Loader2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function PlaygroundPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>('');

  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: () => getModels().then(res => res.data),
  });

  const chatMutation = useMutation({
    mutationFn: (data: { model_id: string; messages: Message[] }) => 
      chatCompletion(data).then(res => res.data),
    onSuccess: (data) => {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response 
      }]);
    },
  });

  const handleSend = () => {
    if (!input.trim() || !selectedModel) return;

    const newMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, newMessage]);
    setInput('');

    chatMutation.mutate({
      model_id: selectedModel,
      messages: [...messages, newMessage],
    });
  };

  const handleClear = () => {
    setMessages([]);
  };

  const downloadedModels = modelsData?.models.filter(
    m => m.download_status === 'downloaded'
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Chat Playground</h1>
        <Button variant="outline" onClick={handleClear} disabled={messages.length === 0}>
          <Trash2 className="mr-2 h-4 w-4" />
          Clear Chat
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        {/* Chat Interface */}
        <Card className="flex flex-col h-[calc(100vh-250px)]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Conversation
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col space-y-4">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 pr-4">
              {messages.length === 0 && (
                <div className="flex items-center justify-center h-full text-center text-muted-foreground">
                  <div>
                    <MessageSquare className="mx-auto h-12 w-12 mb-4 opacity-50" />
                    <p>Select a model and start chatting</p>
                  </div>
                </div>
              )}
              
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}

              {chatMutation.isPending && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-4 py-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              )}
            </div>

            <Separator />

            {/* Input Area */}
            <div className="space-y-2">
              <Textarea
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                rows={3}
                disabled={!selectedModel || chatMutation.isPending}
              />
              <div className="flex justify-between items-center">
                <p className="text-xs text-muted-foreground">
                  Press Enter to send, Shift+Enter for new line
                </p>
                <Button
                  onClick={handleSend}
                  disabled={!input.trim() || !selectedModel || chatMutation.isPending}
                >
                  {chatMutation.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="mr-2 h-4 w-4" />
                  )}
                  Send
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Settings Panel */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Model Selection</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Model</label>
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    {downloadedModels.map((model) => (
                      <SelectItem key={model.model_id} value={model.model_id}>
                        {model.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {downloadedModels.length === 0 && (
                  <p className="text-xs text-destructive">
                    No downloaded models available
                  </p>
                )}
              </div>

              {selectedModel && (
                <div className="pt-2 space-y-2">
                  <Separator />
                  <div className="text-xs space-y-1">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Status</span>
                      <Badge variant="default" className="text-xs">Ready</Badge>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Temperature</label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  defaultValue="0.7"
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">0.7</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Max Tokens</label>
                <input
                  type="number"
                  defaultValue="512"
                  className="w-full px-3 py-2 border rounded-md text-sm"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Messages</span>
                <span className="font-medium">{messages.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Tokens Used</span>
                <span className="font-medium">~{messages.length * 50}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
