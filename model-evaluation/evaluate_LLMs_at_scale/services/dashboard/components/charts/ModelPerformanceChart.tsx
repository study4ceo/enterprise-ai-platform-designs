'use client'

import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export const ModelPerformanceChart = () => {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    // Mock data - in real implementation, fetch from analytics API
    const mockData = [
      { model: 'Gemini', bleu: 0.82, rouge: 0.78, bertscore: 0.89 },
      { model: 'GPT-4', bleu: 0.88, rouge: 0.85, bertscore: 0.92 },
      { model: 'GPT-3.5', bleu: 0.75, rouge: 0.72, bertscore: 0.81 },
      { model: 'Claude', bleu: 0.85, rouge: 0.82, bertscore: 0.90 },
    ]
    setData(mockData)
  }, [])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="model" />
        <YAxis domain={[0, 1]} />
        <Tooltip formatter={(value: number) => value.toFixed(2)} />
        <Legend />
        <Bar dataKey="bleu" fill="#2563eb" name="BLEU" />
        <Bar dataKey="rouge" fill="#10b981" name="ROUGE" />
        <Bar dataKey="bertscore" fill="#f59e0b" name="BERTScore" />
      </BarChart>
    </ResponsiveContainer>
  )
}
