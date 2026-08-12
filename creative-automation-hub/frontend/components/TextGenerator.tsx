'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Send } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface Variant {
  id: number;
  content: string;
}

export default function TextGenerator() {
  const [prompt, setPrompt] = useState('');
  const [type, setType] = useState('social');
  const [tone, setTone] = useState('professional');
  const [variants, setVariants] = useState(3);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Variant[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);

  const { lastMessage } = useWebSocket();

  // Listen for job updates
  useEffect(() => {
    if (lastMessage && lastMessage.job_id === jobId) {
      if (lastMessage.status === 'completed') {
        setResults(lastMessage.output.variants);
        setLoading(false);
      } else if (lastMessage.status === 'failed') {
        alert('Generation failed: ' + lastMessage.error);
        setLoading(false);
      }
    }
  }, [lastMessage, jobId]);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setResults([]);

    try {
      const response = await axios.post(`${API_URL}/api/generate/text`, {
        prompt,
        type,
        tone,
        variants,
        max_length: 500,
      });

      setJobId(response.data.job_id);
    } catch (error) {
      console.error('Generation error:', error);
      alert('Failed to start generation');
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Panel */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6">Generate Text Content</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Write a social media post about sustainable fashion..."
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Content Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary"
            >
              <option value="social">Social Media</option>
              <option value="blog">Blog Post</option>
              <option value="ad">Ad Copy</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary"
            >
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="friendly">Friendly</option>
              <option value="humorous">Humorous</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Variants: {variants}
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={variants}
              onChange={(e) => setVariants(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !prompt.trim()}
            className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Generate
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Panel */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6">Results</h2>

        {results.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            Generated content will appear here
          </div>
        ) : (
          <div className="space-y-4">
            {results.map((variant) => (
              <div
                key={variant.id}
                className="p-4 border rounded-lg hover:border-primary transition cursor-pointer"
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-medium text-gray-500">
                    Variant {variant.id}
                  </span>
                  <button className="text-sm text-primary hover:underline">
                    Copy
                  </button>
                </div>
                <p className="text-gray-700">{variant.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
