import React from 'react'
import { Card, CardContent } from './ui/Card'

interface DeploymentScoreCardProps {
  title: string
  score: number
  weight: number
  color: 'blue' | 'green' | 'red' | 'purple'
}

export const DeploymentScoreCard = ({ 
  title, 
  score, 
  weight,
  color 
}: DeploymentScoreCardProps) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-800 border-blue-300',
    green: 'bg-green-100 text-green-800 border-green-300',
    red: 'bg-red-100 text-red-800 border-red-300',
    purple: 'bg-purple-100 text-purple-800 border-purple-300'
  }

  const barColors = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    red: 'bg-red-600',
    purple: 'bg-purple-600'
  }

  return (
    <Card className={`border-2 ${colorClasses[color]}`}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium">{title}</h3>
          <span className="text-xs opacity-75">{weight}%</span>
        </div>
        <div className="text-3xl font-bold mb-3">
          {score.toFixed(1)}%
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${barColors[color]}`}
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </div>
      </CardContent>
    </Card>
  )
}
