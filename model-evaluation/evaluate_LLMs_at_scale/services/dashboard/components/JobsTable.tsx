import React from 'react'
import { Badge } from './ui/Badge'
import { formatDistanceToNow } from 'date-fns'

interface Job {
  id: string
  name: string
  status: string
  total_tasks: number
  completed_tasks: number
  total_cost_usd: number
  created_at: string
}

interface JobsTableProps {
  jobs: Job[]
  onJobClick: (jobId: string) => void
}

export const JobsTable = ({ jobs, onJobClick }: JobsTableProps) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Progress
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cost
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {jobs.map((job) => {
            const progress = job.total_tasks > 0 
              ? ((job.completed_tasks / job.total_tasks) * 100).toFixed(0)
              : 0

            return (
              <tr
                key={job.id}
                onClick={() => onJobClick(job.id)}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{job.name}</div>
                  <div className="text-xs text-gray-500">{job.id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Badge status={job.status}>{job.status.toUpperCase()}</Badge>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-600">{progress}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  ${job.total_cost_usd.toFixed(4)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
