import React from 'react'
import { Card, CardContent } from './ui/Card'

interface StatsCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  trend?: string
  iconColor?: string
}

export const StatsCard = ({ 
  title, 
  value, 
  icon, 
  trend,
  iconColor = 'text-blue-600'
}: StatsCardProps) => {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600 font-medium">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
            {trend && (
              <p className="text-xs text-gray-500 mt-2">{trend}</p>
            )}
          </div>
          <div className={`p-3 rounded-lg bg-gray-50 ${iconColor}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
