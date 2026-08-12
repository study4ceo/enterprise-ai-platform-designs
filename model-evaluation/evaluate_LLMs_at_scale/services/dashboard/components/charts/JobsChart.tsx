'use client'

import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { api } from '@/lib/api'

export const JobsChart = () => {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    // Mock data - in real implementation, fetch from analytics API
    const mockData = [
      { date: 'Mon', jobs: 12 },
      { date: 'Tue', jobs: 19 },
      { date: 'Wed', jobs: 15 },
      { date: 'Thu', jobs: 25 },
      { date: 'Fri', jobs: 22 },
      { date: 'Sat', jobs: 18 },
      { date: 'Sun', jobs: 14 },
    ]
    setData(mockData)
  }, [])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="jobs" 
          stroke="#2563eb" 
          strokeWidth={2}
          name="Jobs Created"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
