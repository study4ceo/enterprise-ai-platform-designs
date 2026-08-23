'use client';

import { useQuery } from '@tanstack/react-query';
import { getDashboardStats, getTrainingJobs } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { BarChart3, TrendingUp, DollarSign, Clock } from 'lucide-react';

export default function AnalyticsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => getDashboardStats().then(res => res.data),
  });

  const { data: jobs } = useQuery({
    queryKey: ['all-training-jobs'],
    queryFn: () => getTrainingJobs(1, 100).then(res => res.data),
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Analytics</h1>
        <div className="grid gap-4 md:grid-cols-2">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      </div>
    );
  }

  // Calculate metrics
  const completedJobs = jobs?.jobs.filter(j => j.status === 'completed') || [];
  const avgTrainingTime = completedJobs.length > 0
    ? completedJobs.reduce((acc, job) => acc + (job.duration_minutes || 0), 0) / completedJobs.length
    : 0;

  // Estimated cost savings (vs GPT-4 at $30/1M tokens)
  const estimatedTokens = (stats?.total_training_jobs || 0) * 10000000; // 10M tokens per training
  const costSavings = (estimatedTokens / 1000000) * 30; // $30 per 1M tokens

  const successRate = jobs?.total > 0
    ? ((stats?.completed_training_jobs || 0) / jobs.total) * 100
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Analytics</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_training_jobs || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.active_training_jobs || 0} active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{successRate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              {stats?.completed_training_jobs || 0} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Training Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgTrainingTime.toFixed(0)}m</div>
            <p className="text-xs text-muted-foreground">
              Per job average
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cost Savings</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${costSavings.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              vs. GPT-4 API
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Training History */}
      <Card>
        <CardHeader>
          <CardTitle>Training History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {completedJobs.slice(0, 10).map((job) => (
              <div key={job.job_id} className="flex items-center justify-between border-b pb-3 last:border-0">
                <div className="space-y-1">
                  <p className="font-medium">{job.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {job.model_id} • {job.training_method}
                  </p>
                </div>
                <div className="text-right space-y-1">
                  <p className="text-sm font-medium">
                    {job.duration_minutes ? `${job.duration_minutes}min` : 'N/A'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Loss: {job.train_loss ? job.train_loss.toFixed(4) : 'N/A'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Cost Breakdown */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Cost Comparison</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">GPT-4 API (Estimated)</span>
                <span className="font-bold text-destructive">${costSavings.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Local SLM Platform</span>
                <span className="font-bold text-green-600">$0</span>
              </div>
              <div className="h-px bg-border my-2" />
              <div className="flex justify-between">
                <span className="font-medium">Total Savings</span>
                <span className="font-bold text-green-600">${costSavings.toLocaleString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resource Usage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Disk Space</span>
                <span className="text-sm font-medium">
                  {stats?.used_disk_space_gb.toFixed(1)} GB / {stats?.total_disk_space_gb.toFixed(1)} GB
                </span>
              </div>
              <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary transition-all"
                  style={{ 
                    width: `${(stats?.used_disk_space_gb || 0) / (stats?.total_disk_space_gb || 1) * 100}%` 
                  }}
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Models Storage</span>
                <span className="text-sm font-medium">
                  {stats?.models_disk_space_gb.toFixed(1)} GB
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Datasets Storage</span>
                <span className="text-sm font-medium">
                  {stats?.datasets_disk_space_gb.toFixed(1)} GB
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
