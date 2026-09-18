import React from 'react';
import Link from 'next/link';
import { Play, BookOpen, Trophy, Clock, Target, CheckCircle } from 'lucide-react';

/**
 * Landing Page
 * Welcome page with mode selection
 */
export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <div className="bg-black bg-opacity-30 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold text-white">LLM Function Calling Practice</h1>
          <p className="text-gray-300 text-sm mt-1">Master AI Agent Function Calling</p>
        </div>
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-white mb-4">
            Master Production-Level Function Calling
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-6">
            Function calling is what lets an LLM stop just talking and start doing — retrieving live data, 
            triggering real actions, and orchestrating multi-step tasks through connected tools.
          </p>
          <p className="text-lg text-gray-400 max-w-3xl mx-auto">
            Through 600 scenario-based practice questions across six comprehensive tests, build a working, 
            production-level understanding of what it takes to design, orchestrate, secure, and ship reliable function-calling systems.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          <FeatureCard
            icon={<Target className="text-blue-400" size={32} />}
            title="600 Practice Questions"
            description="Six comprehensive test modules covering fundamentals to production patterns"
          />
          <FeatureCard
            icon={<CheckCircle className="text-green-400" size={32} />}
            title="Production-Focused"
            description="Real-world scenarios: security, error handling, orchestration, and scale"
          />
          <FeatureCard
            icon={<Trophy className="text-yellow-400" size={32} />}
            title="Master All Aspects"
            description="From schema design to deployment practices and cost management"
          />
        </div>

        {/* Course Modules Link */}
        <div className="text-center mb-12">
          <Link href="/modules" className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg text-lg font-semibold transition-all transform hover:scale-105 shadow-lg">
              <BookOpen size={24} />
              <span>View All 6 Course Modules (600 Questions)</span>
          </Link>
        </div>

        {/* Mode Selection */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Practice Mode */}
          <Link href="/practice" className="group">
              <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-gray-700 rounded-lg p-8 hover:bg-opacity-20 hover:border-blue-500 transition-all duration-300">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-blue-600 rounded-lg group-hover:scale-110 transition">
                    <Play size={32} className="text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Practice Mode</h3>
                    <p className="text-gray-300 text-sm">Unlimited attempts, hints available</p>
                  </div>
                </div>
                
                <ul className="space-y-2 text-gray-300 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-green-400" />
                    See correct answers
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-green-400" />
                    Get detailed explanations
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-green-400" />
                    No time pressure
                  </li>
                </ul>
                
                <div className="inline-flex items-center gap-2 text-blue-400 font-medium group-hover:gap-3 transition-all">
                  Start Practicing
                  <Play size={16} />
                </div>
              </div>
          </Link>

          {/* Test Mode */}
          <Link href="/test" className="group">
              <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-gray-700 rounded-lg p-8 hover:bg-opacity-20 hover:border-purple-500 transition-all duration-300">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-purple-600 rounded-lg group-hover:scale-110 transition">
                    <Clock size={32} className="text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Test Mode</h3>
                    <p className="text-gray-300 text-sm">Timed simulation, real conditions</p>
                  </div>
                </div>
                
                <ul className="space-y-2 text-gray-300 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-purple-400" />
                    Timed challenges
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-purple-400" />
                    No hints
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-purple-400" />
                    Automatic scoring
                  </li>
                </ul>
                
                <div className="inline-flex items-center gap-2 text-purple-400 font-medium group-hover:gap-3 transition-all">
                  Take a Test
                  <Clock size={16} />
                </div>
              </div>
          </Link>
        </div>

        {/* Tutorial Link */}
        <div className="text-center mt-12">
          <Link href="/tutorial" className="inline-flex items-center gap-2 text-gray-300 hover:text-white transition">
              <BookOpen size={20} />
              <span>Start with the Tutorial if you're new</span>
          </Link>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-black bg-opacity-30 backdrop-blur-sm border-t border-gray-700 py-12">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <StatCard number="600" label="Practice Questions" />
            <StatCard number="6" label="Course Modules" />
            <StatCard number="5" label="Difficulty Levels" />
            <StatCard number="100%" label="Production-Ready" />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-black bg-opacity-30 backdrop-blur-sm border-t border-gray-700 py-6">
        <div className="container mx-auto px-6 text-center text-gray-400 text-sm">
          <p>Practice platform for LLM Function Calling Assessment</p>
          <p className="mt-2">Built to help you ace your AI agent tests 🚀</p>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-gray-700 rounded-lg p-6 text-center">
      <div className="flex justify-center mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-gray-300 text-sm">{description}</p>
    </div>
  );
}

function StatCard({ number, label }) {
  return (
    <div>
      <div className="text-4xl font-bold text-white mb-2">{number}</div>
      <div className="text-gray-300 text-sm">{label}</div>
    </div>
  );
}
