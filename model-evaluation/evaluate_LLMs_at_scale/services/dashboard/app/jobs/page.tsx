'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Search, Filter } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { JobsTable } from '@/components/JobsTable'
import { CreateJobModal } from '@/components/modals/CreateJobModal'
import { api } from '@/lib/api'

interface Job {
  id: string
  name: string
  status: string
  total_tasks: number
  completed_tasks: number
  total_cost_usd: number
  created_at: string
}

export default function JobsPage() {
  const router = useRouter()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    fetchJobs()
    // Refresh every 5 seconds
    const interval = setInterval(fetchJobs, 5000)
    return () => clearInterval(interval)
  }, [statusFilter])

  const fetchJobs = async () => {
    try {
      const params: any = { page: 1, page_size: 50 }
      if (statusFilter !== 'all') {
        params.status = statusFilter
      }
      const data = await api.getJobs(params)
      setJobs(data.jobs)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleJobClick = (jobId: string) => {
    router.push(`/jobs/${jobId}`)
  }

  const handleCreateJob = async (jobData: any) => {
    try {
      await api.createJob(jobData)
      setShowCreateModal(false)
      fetchJobs()
    } catch (error) {
      console.error('Failed to create job:', error)
      alert('Failed to create job. Please try again.')
    }
  }

  const filteredJobs = jobs.filter(job =>
    job.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Evaluation Jobs</h1>
          <p className="text-gray-600 mt-2">
            Manage and monitor your LLM evaluation jobs
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Job
        </Button>
      </div>

      <Card>
        <CardContent className="pt-6">
          {/* Search and Filters */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search jobs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="queued">Queued</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          {/* Jobs Table */}
          {loading ? (
            <div className="text-center py-12">Loading jobs...</div>
          ) : filteredJobs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              No jobs found. Create your first evaluation job!
            </div>
          ) : (
            <JobsTable jobs={filteredJobs} onJobClick={handleJobClick} />
          )}
        </CardContent>
      </Card>

      {/* Create Job Modal */}
      {showCreateModal && (
        <CreateJobModal
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateJob}
        />
      )}
    </div>
  )
}
