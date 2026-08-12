'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Send, Download } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import Image from 'next/image';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

interface ImageVariant {
  id: number;
  url: string;
}

export default function ImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('realistic');
  const [variants, setVariants] = useState(2);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ImageVariant[]>([]);
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
      const response = await axios.post(`${API_URL}/api/generate/image`, {
        prompt,
        width: 1024,
        height: 1024,
        variants,
        style,
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
        <h2 className="text-2xl font-bold mb-6">Generate Images</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A futuristic city at sunset with flying cars..."
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Style</label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary"
            >
              <option value="realistic">Realistic</option>
              <option value="artistic">Artistic</option>
              <option value="anime">Anime</option>
              <option value="digital-art">Digital Art</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Variants: {variants}
            </label>
            <input
              type="range"
              min="1"
              max="4"
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
            Generated images will appear here
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            {results.map((variant) => (
              <div
                key={variant.id}
                className="relative border rounded-lg overflow-hidden hover:border-primary transition group"
              >
                <Image
                  src={variant.url}
                  alt={`Generated image ${variant.id}`}
                  width={512}
                  height={512}
                  className="w-full h-auto"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 p-2 opacity-0 group-hover:opacity-100 transition">
                  <button className="text-white text-sm flex items-center gap-1">
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
