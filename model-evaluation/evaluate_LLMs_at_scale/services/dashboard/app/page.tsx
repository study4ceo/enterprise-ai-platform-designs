'use client'

import { useEffect, useState } from 'react'
import { Activity, DollarSign, Zap, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { StatsCard } from '@/components/StatsCard'
import { JobsChart } from '@/components/charts/JobsChart'
import { CostChart } from '@/components/charts/CostChart'
import { ModelPerformanceChart } from '@/components/charts/ModelPerformanceChart'
import { RecentJobs } from '@/components/RecentJobs'
import { api } from '@/lib/api'

interface DashboardStats {
  totalJobs: number
  activeJobs: number
  completedToday: number
  totalCost: number
  avgLatency: number
  successRate: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardStats()
    // Refresh every 10 seconds
    const interval = setInterval(fetchDashboardStats, 10000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardStats = async () => {
    try {
      const data = await api.getDashboardStats()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Overview of your LLM evaluation system
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Jobs"
          value={stats?.totalJobs || 0}
          icon={<Activity className="h-5 w-5" />}
          trend="+12% from last week"
        />
        <StatsCard
          title="Active Jobs"
          value={stats?.activeJobs || 0}
          icon={<Zap className="h-5 w-5" />}
          trend="Running now"
          iconColor="text-yellow-600"
        />
        <StatsCard
          title="Total Cost"
          value={`$${(stats?.totalCost || 0).toFixed(2)}`}
          icon={<DollarSign className="h-5 w-5" />}
          trend="-5% from last week"
          iconColor="text-green-600"
        />
        <StatsCard
          title="Success Rate"
          value={`${(stats?.successRate || 0).toFixed(1)}%`}
          icon={<TrendingUp className="h-5 w-5" />}
          trend="+2.5% improvement"
          iconColor="text-blue-600"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Job Activity (Last 7 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <JobsChart />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cost Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <CostChart />
          </CardContent>
        </Card>
      </div>

      {/* Model Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Model Performance Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <ModelPerformanceChart />
        </CardContent>
      </Card>

      {/* Recent Jobs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentJobs />
        </CardContent>
      </Card>
    </div>
  )
}
