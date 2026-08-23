'use client';

import { useQuery } from '@tanstack/react-query';
import { getModels } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Cpu, Download, Trash2, HardDrive } from 'lucide-react';

export default function ModelsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['models'],
    queryFn: () => getModels().then(res => res.data),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Models</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'downloaded':
        return 'default';
      case 'downloading':
        return 'secondary';
      case 'not_downloaded':
        return 'outline';
      case 'failed':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Models</h1>
        <Button>
          <Download className="mr-2 h-4 w-4" />
          Download Model
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data?.models.map((model) => (
          <Card key={model.model_id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Cpu className="h-5 w-5 text-primary" />
                  <CardTitle className="text-lg">{model.name}</CardTitle>
                </div>
                {model.is_finetuned && (
                  <Badge variant="secondary">Fine-tuned</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Model ID</span>
                  <span className="font-mono text-xs">{model.model_id}</span>
                </div>
                
                {model.size && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Size</span>
                    <span>{model.size}</span>
                  </div>
                )}

                {model.parameters && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Parameters</span>
                    <span>{(model.parameters / 1e9).toFixed(1)}B</span>
                  </div>
                )}

                {model.disk_size_mb && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Disk Size</span>
                    <span>{(model.disk_size_mb / 1024).toFixed(2)} GB</span>
                  </div>
                )}

                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Status</span>
                  <Badge variant={getStatusColor(model.download_status)}>
                    {model.download_status}
                  </Badge>
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="flex-1"
                  disabled={model.download_status !== 'downloaded'}
                >
                  <Download className="mr-2 h-3 w-3" />
                  Use
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  disabled={!model.is_finetuned}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {data?.models.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <Cpu className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No models found</p>
            <p className="text-sm text-muted-foreground mt-1">
              Download a model to get started
            </p>
            <Button className="mt-4">
              <Download className="mr-2 h-4 w-4" />
              Download Your First Model
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
