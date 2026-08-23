'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Cpu, Database, Zap, MessageSquare, BarChart3 } from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Models', href: '/models', icon: Cpu },
  { name: 'Datasets', href: '/datasets', icon: Database },
  { name: 'Training', href: '/training', icon: Zap },
  { name: 'Playground', href: '/playground', icon: MessageSquare },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col border-r bg-card">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold">🤖 SLM Platform</h1>
      </div>
      
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <Icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      
      <div className="border-t p-4">
        <div className="text-xs text-muted-foreground">
          <div>Version 1.0.0</div>
          <div>Backend: Connected</div>
        </div>
      </div>
    </div>
  );
}
