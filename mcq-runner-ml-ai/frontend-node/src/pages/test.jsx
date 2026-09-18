import React, { useState, useEffect } from 'react';
import TestInterface from '../components/TestInterface';
import { ChevronLeft, ChevronRight, Home, BarChart2, Clock, AlertCircle } from 'lucide-react';
import Link from 'next/link';

/**
 * Test Mode Page
 * Timed test simulation with no hints
 */
export default function TestPage() {
  const [scenarios, setScenarios] = useState([]);
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testStarted, setTestStarted] = useState(false);
  const [totalTimeElapsed, setTotalTimeElapsed] = useState(0);
  const [testCompleted, setTestCompleted] = useState(false);

  // Timer
  useEffect(() => {
    if (!testStarted || testCompleted) return;
    
    const timer = setInterval(() => {
      setTotalTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [testStarted, testCompleted]);

  // Load scenarios
  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      // Load a subset of scenarios for the test
      setScenarios(getTestScenarios());
      setLoading(false);
    } catch (error) {
      console.error('Error loading scenarios:', error);
      setScenarios(getTestScenarios());
      setLoading(false);
    }
  };

  const currentScenario = scenarios[currentScenarioIndex];

  const handleSubmit = (result) => {
    // Save result
    const newResults = [...results, {
      scenarioId: currentScenario.id,
      ...result,
      timestamp: new Date().toISOString()
    }];
    setResults(newResults);

    // Auto-advance to next question
    if (currentScenarioIndex < scenarios.length - 1) {
      setTimeout(() => {
        setCurrentScenarioIndex(currentScenarioIndex + 1);
      }, 2000);
    } else {
      // Test completed
      setTestCompleted(true);
    }
  };

  const startTest = () => {
    setTestStarted(true);
    setTotalTimeElapsed(0);
  };

  const getStats = () => {
    const total = results.length;
    const correct = results.filter(r => r.correct).length;
    const totalScore = results.reduce((sum, r) => sum + (r.score || 0), 0);
    const maxScore = results.length * 100;
    const percentage = maxScore > 0 ? Math.round((totalScore / maxScore) * 100) : 0;
    
    return { total, correct, totalScore, maxScore, percentage };
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-xl">Loading test...</div>
      </div>
    );
  }

  // Pre-test screen
  if (!testStarted) {
    return (
      <div className="h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-6">
          <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-purple-500 rounded-lg p-8">
            <div className="text-center mb-8">
              <Clock size={64} className="mx-auto text-purple-400 mb-4" />
              <h1 className="text-3xl font-bold text-white mb-2">Test Mode</h1>
              <p className="text-gray-300">Real test simulation with time tracking</p>
            </div>

            <div className="space-y-4 mb-8">
              <div className="flex items-start gap-3 text-gray-300">
                <AlertCircle size={20} className="text-purple-400 mt-1 flex-shrink-0" />
                <div>
                  <p className="font-medium text-white">Test Rules:</p>
                  <ul className="mt-2 space-y-1 text-sm">
                    <li>• {scenarios.length} questions total</li>
                    <li>• No hints available</li>
                    <li>• Timer tracks your total time</li>
                    <li>• Each question scored out of 100 points</li>
                    <li>• Auto-advances after submission</li>
                  </ul>
                </div>
              </div>

              <div className="flex items-start gap-3 text-gray-300">
                <AlertCircle size={20} className="text-yellow-400 mt-1 flex-shrink-0" />
                <div>
                  <p className="font-medium text-white">Tips:</p>
                  <ul className="mt-2 space-y-1 text-sm">
                    <li>• Read each query carefully</li>
                    <li>• Review ALL available tools</li>
                    <li>• Double-check your JSON syntax</li>
                    <li>• Stay calm and focused</li>
                  </ul>
                </div>
              </div>
            </div>

            <button
              onClick={startTest}
              className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg transition"
            >
              Start Test
            </button>

            <Link href="/" className="block text-center mt-4 text-gray-300 hover:text-white transition">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Test completed screen
  if (testCompleted) {
    const stats = getStats();
    
    return (
      <div className="h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="max-w-2xl mx-auto px-6">
          <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-purple-500 rounded-lg p-8">
            <div className="text-center mb-8">
              <div className={`text-6xl mb-4 ${stats.percentage >= 70 ? '🎉' : '📊'}`}>
                {stats.percentage >= 90 ? '🏆' : stats.percentage >= 70 ? '🎉' : '📊'}
              </div>
              <h1 className="text-3xl font-bold text-white mb-2">Test Completed!</h1>
              <p className="text-gray-300">Here are your results</p>
            </div>

            <div className="space-y-4 mb-8">
              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4">
                <div className="text-center">
                  <div className="text-5xl font-bold text-purple-400 mb-2">
                    {stats.percentage}%
                  </div>
                  <div className="text-gray-300">Overall Score</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-white mb-1">
                    {stats.correct}/{stats.total}
                  </div>
                  <div className="text-gray-300 text-sm">Correct Answers</div>
                </div>

                <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4 text-center">
                  <div className="text-3xl font-bold text-white mb-1">
                    {formatTime(totalTimeElapsed)}
                  </div>
                  <div className="text-gray-300 text-sm">Total Time</div>
                </div>
              </div>

              <div className="bg-gray-800 bg-opacity-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-300">Points Scored</span>
                  <span className="text-white font-medium">{stats.totalScore} / {stats.maxScore}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${stats.percentage}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-blue-900 bg-opacity-30 border border-blue-500 rounded-lg p-4">
                <p className="text-blue-200 text-sm">
                  {stats.percentage >= 90 ? '🏆 Excellent! You\'re ready for the real test!' :
                   stats.percentage >= 70 ? '🎉 Good job! Practice a bit more to improve.' :
                   '📚 Keep practicing to improve your score.'}
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <Link href="/practice" className="flex-1 py-3 bg-green-600 hover:bg-green-700 text-white text-center font-medium rounded-lg transition">
                Practice More
              </Link>
              <Link href="/" className="flex-1 py-3 bg-gray-600 hover:bg-gray-700 text-white text-center font-medium rounded-lg transition">
                Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const stats = getStats();

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Top Navigation Bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Left: Info */}
          <div className="flex items-center gap-4">
            <div className="text-red-400 font-medium flex items-center gap-2">
              <Clock size={20} />
              Test Mode
            </div>
            
            <div className="text-gray-500">|</div>
            
            <div className="text-white font-mono">
              Question {currentScenarioIndex + 1} / {scenarios.length}
            </div>
          </div>

          {/* Center: Timer */}
          <div className="flex items-center gap-2">
            <Clock size={24} className="text-purple-400" />
            <div className="text-2xl font-mono text-white">
              {formatTime(totalTimeElapsed)}
            </div>
          </div>

          {/* Right: Stats */}
          <div className="flex items-center gap-4">
            <div className="text-gray-300 text-sm">
              Completed: {stats.correct}/{stats.total}
            </div>
          </div>
        </div>
      </div>

      {/* Main Test Interface */}
      <div className="flex-1 overflow-hidden">
        <TestInterface
          key={currentScenario.id}
          scenario={currentScenario}
          onSubmit={handleSubmit}
          mode="test"
        />
      </div>
    </div>
  );
}

/**
 * Get test scenarios
 */
function getTestScenarios() {
  return [
    {
      id: "test_001",
      title: "Weather Query",
      difficulty: "easy",
      category: "Weather API",
      timeLimit: 180,
      points: 100,
      query: "What's the weather like in New York?",
      tools: [
        {
          name: "get_weather",
          description: "Get current weather for a location",
          parameters: {
            type: "object",
            properties: {
              location: {
                type: "string",
                description: "City name or location"
              },
              unit: {
                type: "string",
                enum: ["celsius", "fahrenheit"],
                description: "Temperature unit"
              }
            },
            required: ["location"]
          }
        },
        {
          name: "send_email",
          description: "Send an email",
          parameters: {
            type: "object",
            properties: {
              to: { type: "string" },
              subject: { type: "string" },
              body: { type: "string" }
            },
            required: ["to", "subject", "body"]
          }
        }
      ],
      correct_answer: {
        selected_function: "get_weather",
        arguments: {
          location: "New York"
        }
      },
      explanation: "User asked for current weather in New York, so we use get_weather with location parameter."
    },
    {
      id: "test_002",
      title: "Gratitude - No Function",
      difficulty: "easy",
      category: "Decision Making",
      timeLimit: 120,
      points: 100,
      query: "Thank you so much for your help!",
      tools: [
        {
          name: "send_feedback",
          description: "Send feedback",
          parameters: {
            type: "object",
            properties: {
              message: { type: "string" }
            },
            required: ["message"]
          }
        },
        {
          name: "get_help",
          description: "Get help documentation",
          parameters: {
            type: "object",
            properties: {
              topic: { type: "string" }
            }
          }
        }
      ],
      correct_answer: "N/A",
      explanation: "User is just expressing gratitude, not requesting any action. Answer should be N/A."
    },
    {
      id: "test_003",
      title: "Email Send",
      difficulty: "medium",
      category: "Email API",
      timeLimit: 300,
      points: 100,
      query: "Send an email to sarah@company.com with subject 'Meeting Update' and let her know the meeting is moved to Friday at 2pm",
      tools: [
        {
          name: "send_email",
          description: "Send an email",
          parameters: {
            type: "object",
            properties: {
              to: {
                type: "string",
                description: "Recipient email"
              },
              subject: {
                type: "string",
                description: "Email subject"
              },
              body: {
                type: "string",
                description: "Email body"
              }
            },
            required: ["to", "subject", "body"]
          }
        },
        {
          name: "create_calendar_event",
          description: "Create calendar event",
          parameters: {
            type: "object",
            properties: {
              title: { type: "string" },
              time: { type: "string" }
            },
            required: ["title", "time"]
          }
        }
      ],
      correct_answer: {
        selected_function: "send_email",
        arguments: {
          to: "sarah@company.com",
          subject: "Meeting Update",
          body: "The meeting is moved to Friday at 2pm"
        }
      },
      explanation: "Extract all three parameters from the query: recipient, subject, and body message."
    }
  ];
}
