import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  status?: string
  variant?: 'default' | 'secondary'
  className?: string
}

export const Badge = ({ 
  children, 
  status,
  variant = 'default',
  className = '' 
}: BadgeProps) => {
  const getStatusColor = (status?: string) => {
    if (!status) return 'bg-gray-100 text-gray-800'
    
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'queued':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const colorClass = status ? getStatusColor(status) : ''

  return (
    <span 
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass} ${className}`}
    >
      {children}
    </span>
  )
}
