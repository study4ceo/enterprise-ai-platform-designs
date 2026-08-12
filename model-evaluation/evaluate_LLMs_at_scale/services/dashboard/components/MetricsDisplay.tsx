import React from 'react'

export const MetricsDisplay = ({ results }: { results: any }) => {
  if (!results || !results.metrics) {
    return <div className="text-gray-500">No metrics available</div>
  }

  const metrics = results.metrics

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {Object.entries(metrics).map(([key, value]: [string, any]) => (
        <div key={key} className="p-4 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600 uppercase mb-1">{key}</div>
          <div className="text-2xl font-bold text-gray-900">
            {typeof value === 'number' ? value.toFixed(3) : value}
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${Math.min(value * 100, 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
