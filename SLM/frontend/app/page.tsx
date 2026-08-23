'use client';

import { useQuery } from '@tanstack/react-query';
import { getDashboardStats, checkHealth, getTrainingJobs } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Activity, Cpu, Database, Zap, HardDrive, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => getDashboardStats().then(res => res.data),
    refetchInterval: 5000,
  });

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: () => checkHealth().then(res => res.data),
    refetchInterval: 10000,
  });

  const { data: activeJobs } = useQuery({
    queryKey: ['active-jobs'],
    queryFn: () => getTrainingJobs(1, 5, 'running').then(res => res.data),
    refetchInterval: 3000,
  });

  if (statsLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  const diskUsagePercent = stats 
    ? (stats.used_disk_space_gb / stats.total_disk_space_gb) * 100 
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        {health && (
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-sm text-muted-foreground">
              {health.gpu_available ? `${health.gpu_count} GPU Available` : 'CPU Mode'}
            </span>
          </div>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Models</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_models || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.downloaded_models || 0} downloaded, {stats?.finetuned_models || 0} fine-tuned
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Datasets</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_datasets || 0}</div>
            <p className="text-xs text-muted-foreground">
              Ready for training
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Training Jobs</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_training_jobs || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.completed_training_jobs || 0} completed, {stats?.failed_training_jobs || 0} failed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{diskUsagePercent.toFixed(0)}%</div>
            <p className="text-xs text-muted-foreground">
              {stats?.used_disk_space_gb.toFixed(1)} GB / {stats?.total_disk_space_gb.toFixed(1)} GB
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Active Training Jobs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Active Training Jobs
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activeJobs?.jobs && activeJobs.jobs.length > 0 ? (
            <div className="space-y-4">
              {activeJobs.jobs.map((job) => (
                <div key={job.job_id} className="flex items-center justify-between border-b pb-4 last:border-0">
                  <div className="space-y-1">
                    <p className="font-medium">{job.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {job.model_id} • Epoch {job.current_epoch}/{job.num_epochs || '?'}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge variant="default">
                      {job.progress_percent.toFixed(0)}%
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      Step {job.current_step}/{job.total_steps || '?'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              No active training jobs
            </p>
          )}
        </CardContent>
      </Card>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-1">
              <p className="text-sm font-medium">Database</p>
              <Badge variant={health?.database === 'healthy' ? 'default' : 'destructive'}>
                {health?.database || 'Unknown'}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium">Redis</p>
              <Badge variant={health?.redis === 'healthy' ? 'default' : 'destructive'}>
                {health?.redis || 'Unknown'}
              </Badge>
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium">MinIO</p>
              <Badge variant={health?.minio === 'healthy' ? 'default' : 'destructive'}>
                {health?.minio || 'Unknown'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
