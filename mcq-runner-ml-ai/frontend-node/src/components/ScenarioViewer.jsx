import React, { useState } from 'react';
import { BookOpen, Target, Clock, Award, CheckCircle2, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

/**
 * ScenarioViewer Component
 * Displays scenario details, requirements, and context
 */
export default function ScenarioViewer({ scenario }) {
  const [activeTab, setActiveTab] = useState('description');

  const tabs = [
    { id: 'description', label: 'Description', icon: BookOpen },
    { id: 'requirements', label: 'Requirements', icon: Target },
    { id: 'examples', label: 'Examples', icon: CheckCircle2 },
    { id: 'tips', label: 'Tips', icon: AlertTriangle }
  ];

  const getDifficultyColor = (difficulty) => {
    const colors = {
      easy: 'text-green-400 bg-green-900',
      medium: 'text-yellow-400 bg-yellow-900',
      hard: 'text-red-400 bg-red-900'
    };
    return colors[difficulty] || colors.medium;
  };

  return (
    <div className="h-full bg-gray-900 rounded-lg overflow-hidden flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(scenario.difficulty)}`}>
                {scenario.difficulty?.toUpperCase()}
              </span>
              <span className="px-2 py-1 rounded text-xs font-medium text-blue-400 bg-blue-900">
                {scenario.provider?.toUpperCase()}
              </span>
            </div>
            <h2 className="text-xl font-bold text-white mb-1">
              {scenario.title}
            </h2>
            <p className="text-gray-400 text-sm">
              {scenario.description}
            </p>
          </div>
          
          <div className="flex flex-col items-end gap-2 ml-4">
            <div className="flex items-center gap-2 text-gray-300">
              <Clock size={16} />
              <span className="text-sm">{Math.floor(scenario.timeLimit / 60)} min</span>
            </div>
            <div className="flex items-center gap-2 text-yellow-400">
              <Award size={16} />
              <span className="text-sm font-medium">{scenario.points} pts</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-gray-800 border-b border-gray-700 px-6">
        <div className="flex gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition ${
                  activeTab === tab.id
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'description' && (
          <div className="space-y-6">
            {/* Context */}
            <section>
              <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                <BookOpen size={18} />
                Context
              </h3>
              <div className="bg-gray-800 rounded-lg p-4 text-gray-300">
                <p>{scenario.scenario?.context}</p>
              </div>
            </section>

            {/* Task */}
            <section>
              <h3 className="text-white font-semibold mb-3">Your Task</h3>
              <div className="bg-blue-900 bg-opacity-20 border border-blue-700 rounded-lg p-4 text-blue-200">
                <p>{scenario.scenario?.task}</p>
              </div>
            </section>

            {/* Constraints */}
            {scenario.scenario?.constraints && (
              <section>
                <h3 className="text-white font-semibold mb-3">Constraints</h3>
                <ul className="space-y-2">
                  {scenario.scenario.constraints.map((constraint, index) => (
                    <li key={index} className="flex items-start gap-2 text-gray-300">
                      <span className="text-yellow-400 mt-1">▪</span>
                      <span>{constraint}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Example Usage */}
            {scenario.scenario?.example_usage && (
              <section>
                <h3 className="text-white font-semibold mb-3">Example Usage</h3>
                <div className="bg-gray-800 rounded-lg p-4">
                  <code className="text-green-400 text-sm">
                    {scenario.scenario.example_usage}
                  </code>
                </div>
              </section>
            )}
          </div>
        )}

        {activeTab === 'requirements' && (
          <div className="space-y-3">
            <p className="text-gray-400 text-sm mb-4">
              Your function definition will be evaluated against these requirements:
            </p>
            {scenario.requirements?.map((req) => (
              <div
                key={req.id}
                className={`p-4 rounded-lg border ${
                  req.critical
                    ? 'bg-red-900 bg-opacity-10 border-red-700'
                    : 'bg-gray-800 border-gray-700'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {req.critical && (
                      <AlertTriangle size={16} className="text-red-400" />
                    )}
                    <span className="text-white font-medium">
                      {req.description}
                    </span>
                  </div>
                  <span className="text-gray-400 text-sm">{req.weight}%</span>
                </div>
                {req.critical && (
                  <p className="text-red-400 text-xs mt-2">
                    ⚠️ Critical requirement - must be satisfied
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'examples' && (
          <div className="space-y-6">
            {scenario.solution && (
              <>
                <div className="bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded-lg p-4">
                  <p className="text-yellow-200 text-sm">
                    💡 Examples are hidden until after you submit. Try solving it yourself first!
                  </p>
                </div>
                
                <section>
                  <h3 className="text-white font-semibold mb-3">Function Call Examples</h3>
                  <div className="space-y-3 text-gray-300 text-sm">
                    <p>Here's how the LLM might call your function:</p>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <code className="text-green-400">
                        {scenario.scenario?.example_usage}
                      </code>
                    </div>
                  </div>
                </section>
              </>
            )}
          </div>
        )}

        {activeTab === 'tips' && (
          <div className="space-y-4">
            {/* Common Mistakes */}
            {scenario.common_mistakes && (
              <section>
                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <AlertTriangle size={18} className="text-yellow-400" />
                  Common Mistakes to Avoid
                </h3>
                <div className="space-y-3">
                  {scenario.common_mistakes.map((mistake, index) => (
                    <div key={index} className="bg-gray-800 rounded-lg p-4">
                      <div className="flex items-start gap-2 mb-2">
                        <span className="text-red-400 font-mono text-xs">✗</span>
                        <p className="text-red-300 font-medium">{mistake.mistake}</p>
                      </div>
                      <p className="text-gray-400 text-sm mb-2 ml-5">
                        {mistake.why_wrong}
                      </p>
                      <div className="flex items-start gap-2 ml-5">
                        <span className="text-green-400 font-mono text-xs">✓</span>
                        <p className="text-green-300 text-sm">{mistake.how_to_fix}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Learning Objectives */}
            {scenario.learning_objectives && (
              <section>
                <h3 className="text-white font-semibold mb-3">Learning Objectives</h3>
                <ul className="space-y-2">
                  {scenario.learning_objectives.map((objective, index) => (
                    <li key={index} className="flex items-start gap-2 text-gray-300">
                      <CheckCircle2 size={16} className="text-green-400 mt-1" />
                      <span>{objective}</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
