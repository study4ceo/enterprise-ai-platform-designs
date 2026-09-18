import React from 'react';
import Link from 'next/link';
import { BookOpen, CheckCircle, AlertCircle, Code, Play, ArrowRight } from 'lucide-react';

/**
 * Tutorial Page
 * Step-by-step guide on how to use the platform
 */
export default function TutorialPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <div className="bg-black bg-opacity-30 backdrop-blur-sm border-b border-gray-700">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">Tutorial</h1>
              <p className="text-gray-300 text-sm mt-1">Learn how to master function calling</p>
            </div>
            <Link href="/" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition">
              Back to Home
            </Link>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-6 py-12 max-w-4xl">
        {/* Introduction */}
        <section className="mb-12">
          <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-blue-500 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <BookOpen size={32} className="text-blue-400" />
              <h2 className="text-2xl font-bold text-white">What is Function Calling?</h2>
            </div>
            <p className="text-gray-300 mb-4">
              Function calling is when an AI agent (like ChatGPT or Claude) decides to call external functions/tools 
              to fulfill a user's request. Instead of just responding with text, the AI can take actions like:
            </p>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-start gap-2">
                <CheckCircle size={20} className="text-green-400 mt-1 flex-shrink-0" />
                <span>Getting weather information</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle size={20} className="text-green-400 mt-1 flex-shrink-0" />
                <span>Sending emails</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle size={20} className="text-green-400 mt-1 flex-shrink-0" />
                <span>Creating calendar events</span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle size={20} className="text-green-400 mt-1 flex-shrink-0" />
                <span>Querying databases</span>
              </li>
            </ul>
          </div>
        </section>

        {/* Step 1 */}
        <section className="mb-12">
          <Step number={1} title="Understanding the Interface">
            <p className="text-gray-300 mb-4">
              When you start a practice scenario, you'll see:
            </p>
            <div className="bg-gray-800 rounded-lg p-6 space-y-4">
              <div>
                <h4 className="text-white font-medium mb-2">Left Side: The Query & Tools</h4>
                <ul className="text-gray-300 space-y-2 text-sm">
                  <li>• <strong>Query</strong>: What the user is asking for</li>
                  <li>• <strong>Available Tools</strong>: List of functions you can call</li>
                  <li>• Click on any tool name to see its full schema (parameters, types, descriptions)</li>
                </ul>
              </div>
              <div>
                <h4 className="text-white font-medium mb-2">Right Side: Your Answer</h4>
                <ul className="text-gray-300 space-y-2 text-sm">
                  <li>• <strong>Instructions</strong>: What you need to do</li>
                  <li>• <strong>Editor</strong>: Where you write your answer (JSON or "N/A")</li>
                  <li>• <strong>Submit Button</strong>: Submit when ready</li>
                  <li>• <strong>Feedback</strong>: Appears after submission</li>
                </ul>
              </div>
            </div>
          </Step>
        </section>

        {/* Step 2 */}
        <section className="mb-12">
          <Step number={2} title="Reading the Query">
            <p className="text-gray-300 mb-4">
              The first step is understanding what the user wants. Ask yourself:
            </p>
            <div className="bg-gray-800 rounded-lg p-6 space-y-3">
              <Question>Is the user requesting an ACTION or just making a comment?</Question>
              <Answer>
                <strong>Action:</strong> "Get weather in Boston" → Need function<br />
                <strong>Comment:</strong> "Thanks for your help!" → No function (answer "N/A")
              </Answer>

              <Question>What information did they provide?</Question>
              <Answer>
                Extract key details: locations, names, emails, dates, times, etc.
              </Answer>

              <Question>Is this ONE request or MULTIPLE requests?</Question>
              <Answer>
                <strong>Single:</strong> "Get weather in Boston"<br />
                <strong>Multiple:</strong> "Get weather AND send email"
              </Answer>
            </div>
          </Step>
        </section>

        {/* Step 3 */}
        <section className="mb-12">
          <Step number={3} title="Reviewing Available Tools">
            <p className="text-gray-300 mb-4">
              <strong className="text-yellow-400">IMPORTANT:</strong> Scroll through ALL tools before deciding!
            </p>
            <div className="bg-gray-800 rounded-lg p-6 space-y-4">
              <div>
                <h4 className="text-white font-medium mb-2">How to Review Tools:</h4>
                <ol className="text-gray-300 space-y-2 text-sm list-decimal list-inside">
                  <li>Scroll through the entire list (don't stop at the first few!)</li>
                  <li>Click on relevant tool names to expand their schemas</li>
                  <li>Read the description to understand what each tool does</li>
                  <li>Check the parameters (what inputs it needs)</li>
                  <li>Note which parameters are required vs optional</li>
                </ol>
              </div>
              
              <ExampleBox title="Example Tool Schema">
                <pre className="text-green-400 text-sm overflow-x-auto">{`{
  "name": "send_email",
  "description": "Send an email to a recipient",
  "parameters": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "description": "Recipient email address"
      },
      "subject": {
        "type": "string",
        "description": "Email subject line"
      },
      "body": {
        "type": "string",
        "description": "Email body content"
      }
    },
    "required": ["to", "subject", "body"]
  }
}`}</pre>
                <p className="text-gray-400 text-sm mt-2">
                  This means: You MUST provide "to", "subject", and "body" (all are in the "required" array)
                </p>
              </ExampleBox>
            </div>
          </Step>
        </section>

        {/* Step 4 */}
        <section className="mb-12">
          <Step number={4} title="Writing Your Answer">
            <p className="text-gray-300 mb-4">
              There are three types of answers you can give:
            </p>

            <div className="space-y-6">
              {/* Single Function */}
              <AnswerFormat title="1. Single Function Call" color="blue">
                <p className="text-gray-300 mb-3">When the user needs ONE function:</p>
                <pre className="bg-gray-900 p-4 rounded text-green-400 text-sm overflow-x-auto">{`{
  "selected_function": "get_weather",
  "arguments": {
    "location": "Boston",
    "unit": "fahrenheit"
  }
}`}</pre>
                <p className="text-gray-400 text-sm mt-2">
                  ✅ Extract values from the user query<br />
                  ✅ Include all required parameters<br />
                  ✅ Match parameter types (string, number, boolean, array, object)
                </p>
              </AnswerFormat>

              {/* Multiple Functions */}
              <AnswerFormat title="2. Multiple Function Calls" color="purple">
                <p className="text-gray-300 mb-3">When the user needs MULTIPLE functions:</p>
                <pre className="bg-gray-900 p-4 rounded text-green-400 text-sm overflow-x-auto">{`[
  {
    "selected_function": "get_user_profile",
    "arguments": {}
  },
  {
    "selected_function": "stop_notifications",
    "arguments": {}
  }
]`}</pre>
                <p className="text-gray-400 text-sm mt-2">
                  ✅ Use array format (square brackets)<br />
                  ✅ Each function is a separate object<br />
                  ✅ Order matters (first function runs first)
                </p>
              </AnswerFormat>

              {/* N/A */}
              <AnswerFormat title="3. No Function Needed (N/A)" color="yellow">
                <p className="text-gray-300 mb-3">When NO function is needed:</p>
                <pre className="bg-gray-900 p-4 rounded text-yellow-400 text-sm">N/A</pre>
                <p className="text-gray-400 text-sm mt-2">
                  Use when:<br />
                  ✅ User is just commenting ("Thanks!", "That's helpful!")<br />
                  ✅ User is greeting ("Hello!", "Hi there!")<br />
                  ✅ No matching function available<br />
                  ✅ Not requesting an action
                </p>
              </AnswerFormat>
            </div>
          </Step>
        </section>

        {/* Step 5 */}
        <section className="mb-12">
          <Step number={5} title="Common Mistakes to Avoid">
            <div className="space-y-4">
              <Mistake 
                title="❌ Adding extra fields"
                wrong={`{ "selected_function": "get_weather", "arguments": {...}, "reason": "User asked" }`}
                right={`{ "selected_function": "get_weather", "arguments": {...} }`}
                explanation="Only include 'selected_function' and 'arguments'"
              />

              <Mistake 
                title="❌ Missing required parameters"
                wrong={`{ "selected_function": "send_email", "arguments": { "to": "user@email.com" } }`}
                right={`{ "selected_function": "send_email", "arguments": { "to": "user@email.com", "subject": "Hello", "body": "Message" } }`}
                explanation="Check the 'required' array in the schema"
              />

              <Mistake 
                title="❌ Wrong parameter type"
                wrong={`{ "selected_function": "get_weather", "arguments": { "location": "Boston", "unit": true } }`}
                right={`{ "selected_function": "get_weather", "arguments": { "location": "Boston", "unit": "fahrenheit" } }`}
                explanation="'unit' should be a string, not a boolean"
              />

              <Mistake 
                title="❌ Not scrolling through all tools"
                wrong="Picking the first tool that seems right"
                right="Scrolling through the ENTIRE list to find the best match"
                explanation="Important tools might be at the bottom!"
              />
            </div>
          </Step>
        </section>

        {/* Call to Action */}
        <section>
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Ready to Practice?</h2>
            <p className="text-gray-100 mb-6">
              Start with easy scenarios and work your way up!
            </p>
            <Link href="/practice" className="inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-600 font-medium rounded-lg hover:bg-gray-100 transition">
              <Play size={20} />
              Start Practicing
              <ArrowRight size={20} />
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}

// Helper Components
function Step({ number, title, children }) {
  return (
    <div className="bg-white bg-opacity-10 backdrop-blur-sm border border-gray-700 rounded-lg p-8">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
          {number}
        </div>
        <h3 className="text-xl font-bold text-white">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function Question({ children }) {
  return (
    <div className="flex items-start gap-2">
      <AlertCircle size={20} className="text-blue-400 mt-1 flex-shrink-0" />
      <p className="text-blue-300 font-medium">{children}</p>
    </div>
  );
}

function Answer({ children }) {
  return (
    <div className="ml-7 text-gray-300 text-sm">
      {children}
    </div>
  );
}

function ExampleBox({ title, children }) {
  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <h5 className="text-yellow-400 font-medium mb-2">{title}</h5>
      {children}
    </div>
  );
}

function AnswerFormat({ title, color, children }) {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-900 bg-opacity-20',
    purple: 'border-purple-500 bg-purple-900 bg-opacity-20',
    yellow: 'border-yellow-500 bg-yellow-900 bg-opacity-20'
  };

  return (
    <div className={`border-l-4 ${colorClasses[color]} rounded-r-lg p-6`}>
      <h4 className="text-white font-bold mb-3">{title}</h4>
      {children}
    </div>
  );
}

function Mistake({ title, wrong, right, explanation }) {
  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h5 className="text-red-400 font-medium mb-3">{title}</h5>
      <div className="space-y-2 text-sm">
        <div>
          <span className="text-gray-400">Wrong:</span>
          <pre className="text-red-300 mt-1 overflow-x-auto">{wrong}</pre>
        </div>
        <div>
          <span className="text-gray-400">Right:</span>
          <pre className="text-green-300 mt-1 overflow-x-auto">{right}</pre>
        </div>
        <p className="text-gray-400 italic">{explanation}</p>
      </div>
    </div>
  );
}
