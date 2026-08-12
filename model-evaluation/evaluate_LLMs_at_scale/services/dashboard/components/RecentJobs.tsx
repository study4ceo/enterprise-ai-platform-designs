'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Badge } from './ui/Badge'
import { api } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

export const RecentJobs = () => {
  const router = useRouter()
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      const data = await api.getJobs({ page: 1, page_size: 5 })
      setJobs(data.jobs)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-4">Loading...</div>
  }

  return (
    <div className="space-y-3">
      {jobs.map((job) => (
        <div
          key={job.id}
          onClick={() => router.push(`/jobs/${job.id}`)}
          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
        >
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">{job.name}</h4>
            <p className="text-sm text-gray-500 mt-1">
              {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {job.completed_tasks}/{job.total_tasks}
              </div>
              <div className="text-xs text-gray-500">tasks</div>
            </div>
            <Badge status={job.status}>{job.status}</Badge>
          </div>
        </div>
      ))}
    </div>
  )
}
