import React, { useState, useEffect } from 'react';
import TestInterface from '../components/TestInterface';
import { ChevronLeft, ChevronRight, Home, BarChart2 } from 'lucide-react';
import Link from 'next/link';

/**
 * Practice Page
 * Main practice mode with scenario selection
 */
export default function PracticePage() {
  const [scenarios, setScenarios] = useState([]);
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load scenarios
  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      // In production, this would fetch from an API
      // For now, we'll use imported JSON files
      const scenarioFiles = [
        '/scenarios/easy/weather-simple.json',
        '/scenarios/easy/no-function-needed.json',
        '/scenarios/easy/email-profile-watch.json',
        '/scenarios/medium/email-parameter-extraction.json'
      ];

      const loadedScenarios = await Promise.all(
        scenarioFiles.map(async (file) => {
          const response = await fetch(file);
          return response.json();
        })
      );

      setScenarios(loadedScenarios);
      setLoading(false);
    } catch (error) {
      console.error('Error loading scenarios:', error);
      // Fallback to hardcoded scenarios
      setScenarios(getDefaultScenarios());
      setLoading(false);
    }
  };

  const currentScenario = scenarios[currentScenarioIndex];

  const handleSubmit = (result) => {
    // Save result
    setResults([...results, {
      scenarioId: currentScenario.id,
      ...result,
      timestamp: new Date().toISOString()
    }]);
  };

  const nextScenario = () => {
    if (currentScenarioIndex < scenarios.length - 1) {
      setCurrentScenarioIndex(currentScenarioIndex + 1);
    }
  };

  const previousScenario = () => {
    if (currentScenarioIndex > 0) {
      setCurrentScenarioIndex(currentScenarioIndex - 1);
    }
  };

  const getStats = () => {
    const total = results.length;
    const correct = results.filter(r => r.correct).length;
    const avgTime = results.length > 0
      ? Math.round(results.reduce((sum, r) => sum + r.timeElapsed, 0) / results.length)
      : 0;
    
    return { total, correct, avgTime };
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-xl">Loading scenarios...</div>
      </div>
    );
  }

  if (!currentScenario) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-xl">No scenarios available</div>
      </div>
    );
  }

  const stats = getStats();

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Top Navigation Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Navigation */}
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 text-gray-300 hover:text-white transition">
                <Home size={20} />
                <span>Home</span>
            </Link>
            
            <div className="text-gray-500">|</div>
            
            <div className="text-white font-medium">
              Practice Mode
            </div>
          </div>

          {/* Center: Scenario Navigation */}
          <div className="flex items-center gap-3">
            <button
              onClick={previousScenario}
              disabled={currentScenarioIndex === 0}
              className="p-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded transition"
            >
              <ChevronLeft size={20} />
            </button>
            
            <div className="text-white font-mono">
              {currentScenarioIndex + 1} / {scenarios.length}
            </div>
            
            <button
              onClick={nextScenario}
              disabled={currentScenarioIndex === scenarios.length - 1}
              className="p-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded transition"
            >
              <ChevronRight size={20} />
            </button>
          </div>

          {/* Right: Stats */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-gray-300">
              <BarChart2 size={18} />
              <span className="text-sm">
                {stats.correct}/{stats.total} correct
              </span>
            </div>
            
            {stats.total > 0 && (
              <div className="text-sm text-gray-400">
                Avg: {Math.floor(stats.avgTime / 60)}:{(stats.avgTime % 60).toString().padStart(2, '0')}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Test Interface */}
      <div className="flex-1 overflow-hidden">
        <TestInterface
          key={currentScenario.id}
          scenario={currentScenario}
          onSubmit={handleSubmit}
          mode="practice"
        />
      </div>
    </div>
  );
}

/**
 * Default scenarios (fallback if files don't load)
 */
function getDefaultScenarios() {
  return [
    {
      id: "default_001",
      title: "Weather Query",
      difficulty: "easy",
      category: "Weather",
      timeLimit: 180,
      points: 10,
      query: "What's the weather in Boston?",
      tools: [
        {
          name: "get_weather",
          description: "Get current weather",
          parameters: {
            type: "object",
            properties: {
              location: {
                type: "string",
                description: "City name"
              }
            },
            required: ["location"]
          }
        }
      ],
      correct_answer: {
        selected_function: "get_weather",
        arguments: {
          location: "Boston"
        }
      },
      explanation: "Simple weather query - extract location and call get_weather"
    }
  ];
}
