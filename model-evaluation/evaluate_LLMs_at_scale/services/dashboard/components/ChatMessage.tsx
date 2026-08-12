import React from 'react'
import { User, Bot } from 'lucide-react'
import { format } from 'date-fns'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  data?: any
}

interface ChatMessageProps {
  message: Message
}

export const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-blue-600' : 'bg-gray-200'
      }`}>
        {isUser ? (
          <User className="h-5 w-5 text-white" />
        ) : (
          <Bot className="h-5 w-5 text-gray-600" />
        )}
      </div>

      <div className={`flex-1 ${isUser ? 'flex flex-col items-end' : ''}`}>
        <div className={`rounded-lg px-4 py-3 max-w-3xl ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-100 text-gray-900'
        }`}>
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>
        
        {message.data && !isUser && (
          <div className="mt-2 p-3 bg-white border border-gray-200 rounded-lg max-w-3xl">
            <p className="text-xs font-medium text-gray-600 mb-2">Related Data:</p>
            <pre className="text-xs text-gray-700 overflow-x-auto">
              {JSON.stringify(message.data, null, 2)}
            </pre>
          </div>
        )}
        
        <p className="text-xs text-gray-500 mt-1">
          {format(message.timestamp, 'HH:mm')}
        </p>
      </div>
    </div>
  )
}
