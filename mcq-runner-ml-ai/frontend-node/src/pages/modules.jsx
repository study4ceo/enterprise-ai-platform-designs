import React from 'react';
import Link from 'next/link';
import { BookOpen, Lock, CheckCircle, Play, Clock, Target } from 'lucide-react';

/**
 * Course Modules Page
 * Shows all 6 comprehensive test modules
 */
export default function ModulesPage() {
  const modules = [
    {
      id: 1,
      title: "Function Calling Fundamentals & Schema Design",
      description: "JSON schema design, parameter types, naming conventions, and required vs. optional fields",
      topics: [
        "Understanding JSON schema structure",
        "Parameter types: string, number, boolean, array, object",
        "Naming conventions and best practices",
        "Required vs optional fields",
        "Default values and validation rules",
        "Schema documentation practices"
      ],
      questions: 100,
      difficulty: "Beginner",
      estimatedTime: "2-3 hours",
      unlocked: true
    },
    {
      id: 2,
      title: "Tool Selection & Multi-Tool Orchestration",
      description: "Disambiguation, routing architecture, and combining results across multiple tools",
      topics: [
        "Tool selection strategy",
        "Function disambiguation techniques",
        "Routing architecture patterns",
        "Multi-tool orchestration",
        "Combining results across tools",
        "Tool dependencies and sequencing"
      ],
      questions: 100,
      difficulty: "Intermediate",
      estimatedTime: "3-4 hours",
      unlocked: true
    },
    {
      id: 3,
      title: "Structured Output & Parameter Validation",
      description: "Type validation, malformed output handling, and constrained generation techniques",
      topics: [
        "Output structure validation",
        "Type checking and coercion",
        "Handling malformed outputs",
        "Constrained generation techniques",
        "Output parsing strategies",
        "Graceful degradation patterns"
      ],
      questions: 100,
      difficulty: "Intermediate",
      estimatedTime: "3-4 hours",
      unlocked: true
    },
    {
      id: 4,
      title: "Agentic Workflows & Tool Chaining",
      description: "State management, task decomposition, self-correction, and multi-step failure handling",
      topics: [
        "State management patterns",
        "Task decomposition strategies",
        "Tool chaining architectures",
        "Self-correction mechanisms",
        "Multi-step failure handling",
        "Workflow orchestration patterns"
      ],
      questions: 100,
      difficulty: "Advanced",
      estimatedTime: "4-5 hours",
      unlocked: false
    },
    {
      id: 5,
      title: "Error Handling, Reliability & Security",
      description: "Retries, timeouts, prompt injection defenses, and access control for tool execution",
      topics: [
        "Retry strategies and exponential backoff",
        "Timeout handling and circuit breakers",
        "Prompt injection attack patterns",
        "Input sanitization techniques",
        "Access control for tool execution",
        "Audit logging and monitoring"
      ],
      questions: 100,
      difficulty: "Advanced",
      estimatedTime: "4-5 hours",
      unlocked: false
    },
    {
      id: 6,
      title: "Production Patterns",
      description: "Testing strategy, observability, API design, deployment practices, and cost management at scale",
      topics: [
        "Testing strategies for function calling",
        "Observability and monitoring",
        "API design best practices",
        "Deployment patterns",
        "Cost optimization techniques",
        "Scaling considerations"
      ],
      questions: 100,
      difficulty: "Expert",
      estimatedTime: "5-6 hours",
      unlocked: false
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <div className="bg-black bg-opacity-30 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Course Modules</h1>
              <p className="text-gray-300 text-sm mt-1">600 questions across 6 comprehensive modules</p>
            </div>
            <Link href="/" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition">
              Back to Home
            </Link>
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="bg-black bg-opacity-20 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-6 py-6">
          <div className="grid md:grid-cols-4 gap-6">
            <StatCard label="Total Questions" value="600" />
            <StatCard label="Completed" value="0" />
            <StatCard label="Pass Rate" value="-" />
            <StatCard label="Time Spent" value="0h" />
          </div>
        </div>
      </div>

      {/* Modules List */}
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-5xl mx-auto space-y-6">
          {modules.map((module, index) => (
            <ModuleCard key={module.id} module={module} index={index} />
          ))}
        </div>

        {/* Learning Path Info */}
        <div className="max-w-5xl mx-auto mt-12 bg-blue-900 bg-opacity-30 border border-blue-500 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <Target size={32} className="text-blue-400 flex-shrink-0" />
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Recommended Learning Path</h3>
              <p className="text-gray-300 mb-4">
                Complete modules sequentially for the best learning experience. Each module builds on concepts 
                from previous ones. Modules unlock after achieving 70% or higher on the previous module's test.
              </p>
              <ul className="space-y-2 text-gray-300 text-sm">
                <li>✓ Start with fundamentals to build a strong foundation</li>
                <li>✓ Practice in realistic scenarios, not just theory</li>
                <li>✓ Focus on production patterns early to avoid bad habits</li>
                <li>✓ Review wrong answers and understand why they failed</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ModuleCard({ module, index }) {
  const difficultyColors = {
    'Beginner': 'text-green-400 border-green-500',
    'Intermediate': 'text-blue-400 border-blue-500',
    'Advanced': 'text-purple-400 border-purple-500',
    'Expert': 'text-red-400 border-red-500'
  };

  return (
    <div className={`bg-white bg-opacity-10 backdrop-blur-sm border ${module.unlocked ? 'border-gray-700' : 'border-gray-800'} rounded-lg overflow-hidden ${!module.unlocked && 'opacity-60'}`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                {module.id}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">{module.title}</h3>
                <div className="flex items-center gap-3 mt-1">
                  <span className={`text-xs px-2 py-1 rounded border ${difficultyColors[module.difficulty]}`}>
                    {module.difficulty}
                  </span>
                  <span className="text-gray-400 text-xs flex items-center gap-1">
                    <Clock size={14} />
                    {module.estimatedTime}
                  </span>
                </div>
              </div>
            </div>
            <p className="text-gray-300 text-sm mt-2">{module.description}</p>
          </div>
          
          {!module.unlocked && (
            <Lock size={24} className="text-gray-500 ml-4" />
          )}
        </div>

        {/* Topics */}
        <div className="mb-6">
          <h4 className="text-white font-medium mb-3">Topics Covered:</h4>
          <div className="grid md:grid-cols-2 gap-2">
            {module.topics.map((topic, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <CheckCircle size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>{topic}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-700">
          <div className="text-gray-300 text-sm">
            {module.questions} Questions
          </div>
          
          {module.unlocked ? (
            <Link href={`/module/${module.id}`} className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition">
              <Play size={16} />
              Start Module
            </Link>
          ) : (
            <button disabled className="inline-flex items-center gap-2 px-4 py-2 bg-gray-700 text-gray-400 rounded cursor-not-allowed">
              <Lock size={16} />
              Locked
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar (if started) */}
      {module.unlocked && module.id <= 3 && (
        <div className="bg-gray-800 bg-opacity-50 px-6 py-3">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
            <span>Progress</span>
            <span>0 / {module.questions}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div className="bg-blue-500 h-2 rounded-full" style={{ width: '0%' }}></div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-gray-700 rounded-lg p-4 text-center">
      <div className="text-3xl font-bold text-white mb-1">{value}</div>
      <div className="text-gray-300 text-sm">{label}</div>
    </div>
  );
}
