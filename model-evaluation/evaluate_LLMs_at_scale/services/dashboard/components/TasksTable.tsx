import React from 'react'
import { Badge } from './ui/Badge'

export const TasksTable = ({ tasks }: { tasks: any[] }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Model</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Latency</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tokens</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {tasks.map((task) => (
            <tr key={task.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {task.model}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <Badge status={task.status}>{task.status}</Badge>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {task.latency_ms ? `${task.latency_ms}ms` : '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {task.cost_usd ? `$${task.cost_usd.toFixed(4)}` : '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {task.tokens_used || '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
