import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, CheckCircle, XCircle, AlertCircle, Clock } from 'lucide-react';
import Editor from '@monaco-editor/react';
import toast from 'react-hot-toast';

/**
 * TestInterface Component
 * Exact replica of Turing function calling test interface
 */
export default function TestInterface({ scenario, onSubmit, mode = 'practice' }) {
  const [expandedTools, setExpandedTools] = useState(new Set());
  const [answer, setAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isRunning, setIsRunning] = useState(true);

  // Timer
  useEffect(() => {
    if (!isRunning) return;
    
    const timer = setInterval(() => {
      setTimeElapsed(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [isRunning]);

  // Toggle tool expansion
  const toggleTool = (toolName) => {
    setExpandedTools(prev => {
      const newSet = new Set(prev);
      if (newSet.has(toolName)) {
        newSet.delete(toolName);
      } else {
        newSet.add(toolName);
      }
      return newSet;
    });
  };

  // Validate and submit answer
  const handleSubmit = async () => {
    setIsRunning(false);
    
    try {
      // Try to parse answer if it's JSON
      let parsedAnswer;
      const trimmedAnswer = answer.trim();
      
      if (trimmedAnswer === 'N/A') {
        parsedAnswer = 'N/A';
      } else {
        try {
          parsedAnswer = JSON.parse(trimmedAnswer);
        } catch (e) {
          toast.error('Invalid JSON format');
          return;
        }
      }

      // Evaluate answer
      const evaluation = evaluateAnswer(parsedAnswer, scenario);
      setResult(evaluation);
      setSubmitted(true);

      if (evaluation.correct) {
        toast.success('Correct! ✅');
      } else {
        toast.error('Incorrect. Review the feedback.');
      }

      // Call parent submit handler
      if (onSubmit) {
        onSubmit({
          answer: parsedAnswer,
          timeElapsed,
          correct: evaluation.correct,
          score: evaluation.score
        });
      }
    } catch (error) {
      toast.error('Submission error: ' + error.message);
    }
  };

  // Reset for next attempt (practice mode only)
  const handleReset = () => {
    setAnswer('');
    setSubmitted(false);
    setResult(null);
    setTimeElapsed(0);
    setIsRunning(true);
  };

  // Format time display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Function Calling Practice</h1>
            <p className="text-sm text-gray-600 mt-1">
              {scenario.category} - {scenario.difficulty}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-gray-700">
              <Clock size={20} />
              <span className="font-mono text-lg">{formatTime(timeElapsed)}</span>
            </div>
            {mode === 'test' && scenario.timeLimit && (
              <div className="text-sm text-gray-600">
                Time Limit: {Math.floor(scenario.timeLimit / 60)} min
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content - Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side - Query and Tools */}
        <div className="w-1/2 border-r border-gray-200 flex flex-col bg-gray-900">
          {/* Query Section */}
          <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white mb-3">Query</h2>
            <div className="bg-gray-900 rounded-lg p-4">
              <p className="text-white text-base leading-relaxed">
                {scenario.query}
              </p>
            </div>
          </div>

          {/* Available Tools */}
          <div className="flex-1 overflow-y-auto">
            <div className="px-6 py-4">
              <h2 className="text-lg font-semibold text-cyan-400 mb-3">
                Available Tools
              </h2>
              <p className="text-gray-400 text-sm mb-4">
                Here's the list of all the available function calls
              </p>

              {/* Tool List */}
              <div className="space-y-2">
                {scenario.tools.map((tool) => (
                  <div key={tool.name} className="border border-gray-700 rounded">
                    {/* Tool Header */}
                    <button
                      onClick={() => toggleTool(tool.name)}
                      className="w-full flex items-center gap-2 px-4 py-3 bg-gray-800 hover:bg-gray-750 transition text-left"
                    >
                      {expandedTools.has(tool.name) ? (
                        <ChevronDown size={18} className="text-gray-400" />
                      ) : (
                        <ChevronRight size={18} className="text-gray-400" />
                      )}
                      <span className="text-white font-mono">{tool.name}</span>
                    </button>

                    {/* Tool Schema (Expanded) */}
                    {expandedTools.has(tool.name) && (
                      <div className="bg-gray-900 px-4 py-3 border-t border-gray-700">
                        <p className="text-gray-300 text-sm font-semibold mb-2">
                          Tool Call Schema
                        </p>
                        <pre className="text-sm text-gray-300 overflow-x-auto">
                          {JSON.stringify(tool, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Answer Input */}
        <div className="w-1/2 flex flex-col bg-white">
          {/* Instructions */}
          <div className="bg-blue-50 border-b border-blue-200 px-6 py-4">
            <h3 className="font-semibold text-blue-900 mb-2">Instructions</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Review the query and available tools</li>
              <li>• Decide which function(s) to call, or respond with "N/A"</li>
              <li>• Write the JSON payload with correct arguments</li>
              <li>• Verify your JSON syntax before submitting</li>
            </ul>
          </div>

          {/* Answer Editor */}
          <div className="flex-1 flex flex-col">
            <div className="bg-gray-100 px-6 py-3 border-b border-gray-300">
              <h3 className="font-semibold text-gray-900">Your Answer</h3>
              <p className="text-sm text-gray-600 mt-1">
                Enter your function call(s) or "N/A"
              </p>
            </div>

            <div className="flex-1 overflow-hidden">
              <Editor
                height="100%"
                defaultLanguage="json"
                theme="light"
                value={answer}
                onChange={(value) => setAnswer(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 2,
                  readOnly: submitted && mode === 'test'
                }}
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="bg-gray-50 border-t border-gray-300 px-6 py-4">
            <div className="flex items-center gap-3">
              {!submitted ? (
                <button
                  onClick={handleSubmit}
                  disabled={!answer.trim()}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded transition"
                >
                  Submit Answer
                </button>
              ) : (
                <>
                  {mode === 'practice' && (
                    <button
                      onClick={handleReset}
                      className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded transition"
                    >
                      Try Another Question
                    </button>
                  )}
                </>
              )}
              
              <span className="text-sm text-gray-600">
                {answer.trim() ? `${answer.length} characters` : 'Enter your answer'}
              </span>
            </div>
          </div>

          {/* Feedback (After Submission) */}
          {submitted && result && (
            <div className={`border-t-4 px-6 py-4 ${
              result.correct ? 'bg-green-50 border-green-500' : 'bg-red-50 border-red-500'
            }`}>
              <div className="flex items-start gap-3">
                {result.correct ? (
                  <CheckCircle className="text-green-600 flex-shrink-0 mt-1" size={24} />
                ) : (
                  <XCircle className="text-red-600 flex-shrink-0 mt-1" size={24} />
                )}
                
                <div className="flex-1">
                  <h4 className={`font-semibold mb-2 ${
                    result.correct ? 'text-green-900' : 'text-red-900'
                  }`}>
                    {result.correct ? 'Correct!' : 'Incorrect'}
                  </h4>
                  
                  <div className="text-sm space-y-2">
                    {result.feedback.map((item, index) => (
                      <div key={index} className={
                        result.correct ? 'text-green-800' : 'text-red-800'
                      }>
                        {item}
                      </div>
                    ))}
                  </div>

                  {!result.correct && mode === 'practice' && (
                    <div className="mt-4 p-3 bg-white rounded border border-gray-300">
                      <p className="font-medium text-gray-900 mb-2">Correct Answer:</p>
                      <pre className="text-sm text-gray-800 overflow-x-auto">
                        {JSON.stringify(scenario.correct_answer, null, 2)}
                      </pre>
                    </div>
                  )}

                  {scenario.explanation && mode === 'practice' && (
                    <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
                      <p className="font-medium text-blue-900 mb-1">Explanation:</p>
                      <p className="text-sm text-blue-800">{scenario.explanation}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Evaluate user's answer against correct answer
 */
function evaluateAnswer(userAnswer, scenario) {
  const correctAnswer = scenario.correct_answer;
  const feedback = [];
  let correct = false;
  let score = 0;

  // Handle N/A case
  if (correctAnswer === 'N/A') {
    if (userAnswer === 'N/A') {
      feedback.push('✅ Correctly identified that no function call is needed');
      correct = true;
      score = 100;
    } else {
      feedback.push('❌ No function call was needed. Should respond with "N/A"');
      feedback.push(`Reason: ${scenario.explanation || 'The query does not require a function call'}`);
    }
    return { correct, feedback, score };
  }

  // Handle function call case
  if (userAnswer === 'N/A') {
    feedback.push('❌ A function call was needed, but you responded with "N/A"');
    feedback.push(`Expected function: ${correctAnswer.selected_function || 'multiple functions'}`);
    return { correct, feedback, score };
  }

  // Compare function selection
  if (userAnswer.selected_function === correctAnswer.selected_function) {
    feedback.push('✅ Correct function selected');
    score += 40;
  } else {
    feedback.push(`❌ Wrong function. Expected: ${correctAnswer.selected_function}, Got: ${userAnswer.selected_function}`);
    return { correct, feedback, score };
  }

  // Compare arguments
  const userArgs = userAnswer.arguments || {};
  const correctArgs = correctAnswer.arguments || {};
  
  const userKeys = Object.keys(userArgs);
  const correctKeys = Object.keys(correctArgs);

  // Check for missing required arguments
  const missingKeys = correctKeys.filter(k => !userKeys.includes(k));
  if (missingKeys.length > 0) {
    feedback.push(`❌ Missing required argument(s): ${missingKeys.join(', ')}`);
    return { correct, feedback, score };
  }

  // Check for extra arguments
  const extraKeys = userKeys.filter(k => !correctKeys.includes(k));
  if (extraKeys.length > 0) {
    feedback.push(`⚠️ Extra argument(s) provided: ${extraKeys.join(', ')}`);
    score -= 10;
  }

  // Check argument values
  let allArgsCorrect = true;
  for (const key of correctKeys) {
    if (JSON.stringify(userArgs[key]) === JSON.stringify(correctArgs[key])) {
      feedback.push(`✅ Correct value for '${key}'`);
      score += Math.floor(40 / correctKeys.length);
    } else {
      feedback.push(`❌ Wrong value for '${key}'. Expected: ${JSON.stringify(correctArgs[key])}, Got: ${JSON.stringify(userArgs[key])}`);
      allArgsCorrect = false;
    }
  }

  // JSON structure check
  score += 20; // Bonus for valid JSON structure

  correct = allArgsCorrect && missingKeys.length === 0;
  score = Math.max(0, Math.min(100, score));

  return { correct, feedback, score };
}
