'use client'

import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444']

export const CostChart = () => {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    // Mock data - in real implementation, fetch from analytics API
    const mockData = [
      { name: 'Gemini Pro', value: 45.50 },
      { name: 'GPT-4', value: 120.30 },
      { name: 'GPT-3.5', value: 25.20 },
      { name: 'Claude', value: 80.40 },
    ]
    setData(mockData)
  }, [])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
      </PieChart>
    </ResponsiveContainer>
  )
}
