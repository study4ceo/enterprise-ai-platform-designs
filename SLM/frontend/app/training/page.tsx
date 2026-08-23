'use client';

import { useQuery } from '@tanstack/react-query';
import { getTrainingJobs } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { Zap, Play, Pause, X, Plus, Clock, Cpu } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function TrainingPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['training-jobs'],
    queryFn: () => getTrainingJobs().then(res => res.data),
    refetchInterval: 3000, // Refresh every 3 seconds for real-time updates
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Training</h1>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'running':
        return 'default';
      case 'completed':
        return 'secondary';
      case 'queued':
        return 'outline';
      case 'failed':
        return 'destructive';
      case 'cancelled':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Play className="h-3 w-3" />;
      case 'queued':
        return <Clock className="h-3 w-3" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Training Jobs</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Training Job
        </Button>
      </div>

      <div className="space-y-4">
        {data?.jobs.map((job) => (
          <Card key={job.job_id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Zap className="h-5 w-5 text-primary" />
                  <div>
                    <CardTitle className="text-lg">{job.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {job.model_id} • {job.training_method.toUpperCase()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={getStatusVariant(job.status)}>
                    {getStatusIcon(job.status)}
                    <span className="ml-1">{job.status.toUpperCase()}</span>
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Progress Bar */}
              {(job.status === 'running' || job.status === 'queued') && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">{job.progress_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={job.progress_percent} className="h-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Step {job.current_step}/{job.total_steps || '?'}</span>
                    <span>Epoch {job.current_epoch}/{job.num_epochs || '?'}</span>
                  </div>
                </div>
              )}

              <Separator />

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Training Loss</p>
                  <p className="text-lg font-semibold">
                    {job.train_loss ? job.train_loss.toFixed(4) : '—'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Eval Loss</p>
                  <p className="text-lg font-semibold">
                    {job.eval_loss ? job.eval_loss.toFixed(4) : '—'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">GPU</p>
                  <p className="text-sm font-medium flex items-center gap-1">
                    <Cpu className="h-3 w-3" />
                    {job.gpu_type || 'N/A'}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Started</p>
                  <p className="text-sm font-medium">
                    {job.started_at 
                      ? formatDistanceToNow(new Date(job.started_at), { addSuffix: true })
                      : 'Not started'
                    }
                  </p>
                </div>
              </div>

              {/* Error Message */}
              {job.status === 'failed' && job.error_message && (
                <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
                  <p className="font-medium">Error:</p>
                  <p className="text-xs mt-1 font-mono">{job.error_message.substring(0, 200)}...</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2 pt-2">
                {job.status === 'running' && (
                  <>
                    <Button variant="outline" size="sm">
                      <Pause className="mr-2 h-3 w-3" />
                      Pause
                    </Button>
                    <Button variant="outline" size="sm">
                      <X className="mr-2 h-3 w-3" />
                      Cancel
                    </Button>
                  </>
                )}
                {job.status === 'completed' && (
                  <Button variant="outline" size="sm">
                    View Results
                  </Button>
                )}
                <Button variant="ghost" size="sm" className="ml-auto">
                  View Logs
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {data?.jobs.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Zap className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No training jobs yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Start training your first model
            </p>
            <Button className="mt-4">
              <Plus className="mr-2 h-4 w-4" />
              Create Training Job
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
