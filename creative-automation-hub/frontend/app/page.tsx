'use client';

import { useState } from 'react';
import { Sparkles, Image as ImageIcon, Type } from 'lucide-react';
import TextGenerator from '@/components/TextGenerator';
import ImageGenerator from '@/components/ImageGenerator';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'text' | 'image'>('text');

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="w-10 h-10 text-primary" />
            <h1 className="text-4xl font-bold text-gray-900">
              Creative Automation Hub
            </h1>
          </div>
          <p className="text-lg text-gray-600">
            AI-powered content generation at scale
          </p>
        </header>

        {/* Tab Navigation */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() => setActiveTab('text')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'text'
                ? 'bg-primary text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <Type className="w-5 h-5" />
            Text Generator
          </button>
          <button
            onClick={() => setActiveTab('image')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'image'
                ? 'bg-primary text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50'
            }`}
          >
            <ImageIcon className="w-5 h-5" />
            Image Generator
          </button>
        </div>

        {/* Content */}
        <div className="max-w-6xl mx-auto">
          {activeTab === 'text' ? <TextGenerator /> : <ImageGenerator />}
        </div>
      </div>
    </main>
  );
}
