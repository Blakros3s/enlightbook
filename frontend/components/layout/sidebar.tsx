'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/components/auth/auth-provider';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  School,
  LayoutDashboard,
  Users,
  GraduationCap,
  Calendar,
  BookOpen,
  Wallet,
  FileText,
  CheckSquare,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Menu,
  Shield,
  UserCircle,
  Building,
  Layers,
  Award,
  ClipboardList,
  MessageSquare,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  roles: string[];
  badge?: string | number;
  children?: NavItem[];
}

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const navigationItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['master', 'principal', 'coordinator', 'teacher', 'student', 'accountant'],
  },
  {
    label: 'Users',
    href: '/users',
    icon: Users,
    roles: ['master', 'principal'],
    children: [
      { label: 'All Users', href: '/users', icon: Users, roles: ['master', 'principal'] },
      { label: 'Teachers', href: '/teachers', icon: GraduationCap, roles: ['master', 'principal'] },
      { label: 'Students', href: '/students', icon: UserCircle, roles: ['master', 'principal', 'teacher'] },
    ],
  },
  {
    label: 'Academic',
    href: '/academic',
    icon: BookOpen,
    roles: ['master', 'principal', 'coordinator', 'teacher'],
    children: [
      { label: 'Academic Years', href: '/academic/years', icon: Calendar, roles: ['master', 'principal'] },
      { label: 'Classes', href: '/academic/classes', icon: Building, roles: ['master', 'principal', 'coordinator'] },
      { label: 'Subjects', href: '/academic/subjects', icon: Layers, roles: ['master', 'principal', 'coordinator'] },
      { label: 'Enrollments', href: '/academic/enrollments', icon: Users, roles: ['master', 'principal', 'coordinator'] },
    ],
  },
  {
    label: 'Finance',
    href: '/finance',
    icon: Wallet,
    roles: ['master', 'principal', 'accountant'],
    children: [
      { label: 'Fee Structure', href: '/finance/fees', icon: FileText, roles: ['master', 'principal', 'accountant'] },
      { label: 'Bills', href: '/finance/bills', icon: ClipboardList, roles: ['master', 'principal', 'accountant'] },
      { label: 'Payments', href: '/finance/payments', icon: Wallet, roles: ['master', 'principal', 'accountant'] },
      { label: 'Scholarships', href: '/finance/scholarships', icon: Award, roles: ['master', 'principal', 'accountant'] },
    ],
  },
  {
    label: 'Examinations',
    href: '/exams',
    icon: FileText,
    roles: ['master', 'principal', 'coordinator', 'teacher'],
    children: [
      { label: 'Grading Scales', href: '/exams/grading', icon: Award, roles: ['master', 'principal'] },
      { label: 'Exams', href: '/exams/list', icon: FileText, roles: ['master', 'principal', 'coordinator', 'teacher'] },
      { label: 'Results', href: '/exams/results', icon: ClipboardList, roles: ['master', 'principal', 'coordinator', 'teacher'] },
      { label: 'Report Cards', href: '/exams/report-cards', icon: FileText, roles: ['master', 'principal', 'teacher'] },
    ],
  },
  {
    label: 'Attendance',
    href: '/attendance',
    icon: CheckSquare,
    roles: ['master', 'principal', 'coordinator', 'teacher'],
    children: [
      { label: 'Daily', href: '/attendance/daily', icon: Calendar, roles: ['master', 'principal', 'coordinator', 'teacher'] },
      { label: 'Period-wise', href: '/attendance/period', icon: ClockIcon, roles: ['master', 'principal', 'coordinator', 'teacher'] },
      { label: 'Leave Requests', href: '/attendance/leaves', icon: FileText, roles: ['master', 'principal', 'teacher'] },
      { label: 'Reports', href: '/attendance/reports', icon: BarChartIcon, roles: ['master', 'principal', 'coordinator'] },
    ],
  },
  {
    label: 'Messages',
    href: '/messages',
    icon: MessageSquare,
    roles: ['master', 'principal', 'coordinator', 'teacher', 'student', 'parent'],
    badge: 0,
  },
  {
    label: 'Settings',
    href: '/settings',
    icon: Settings,
    roles: ['master', 'principal'],
  },
];

// Helper icon components
function ClockIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </svg>
  );
}

function BarChartIcon(props: any) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="20" x2="12" y2="10"/>
      <line x1="18" y1="20" x2="18" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="16"/>
    </svg>
  );
}

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const router = useRouter();
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 1024);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const hasRole = (roles: string[]) => {
    if (!user) return false;
    return roles.some(role => user.roles.includes(role));
  };

  const toggleExpand = (label: string) => {
    setExpandedItems(prev =>
      prev.includes(label) ? prev.filter(i => i !== label) : [...prev, label]
    );
  };

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const visibleNavItems = navigationItems.filter(item => hasRole(item.roles));

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          'fixed left-0 top-0 z-40 h-screen bg-card border-r transition-all duration-300 ease-in-out',
          isOpen ? 'w-72' : 'w-20',
          isMobile && !isOpen && '-translate-x-full'
        )}
      >
        {/* Logo Section */}
        <div className="h-16 flex items-center justify-between px-4 border-b">
          <Link 
            href="/dashboard" 
            className={cn(
              'flex items-center gap-3 transition-all duration-300',
              !isOpen && 'justify-center'
            )}
          >
            <div className="flex items-center justify-center w-10 h-10 rounded-xl gradient-primary shadow-lg shadow-blue-500/25">
              <School className="w-6 h-6 text-white" />
            </div>
            <span
              className={cn(
                'font-bold text-lg gradient-text whitespace-nowrap overflow-hidden transition-all duration-300',
                !isOpen && 'w-0 opacity-0'
              )}
            >
              EnlightBook
            </span>
          </Link>
          
          {!isMobile && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onToggle}
              className="shrink-0"
            >
              {isOpen ? (
                <ChevronLeft className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>

        {/* Navigation */}
        <ScrollArea className="flex-1 h-[calc(100vh-8rem)] py-4">
          <nav className="px-3 space-y-1">
            {visibleNavItems.map((item) => {
              const active = isActive(item.href);
              const hasChildren = item.children && item.children.length > 0;
              const isExpanded = expandedItems.includes(item.label);

              return (
                <div key={item.label}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Link
                        href={hasChildren ? '#' : item.href}
                        onClick={(e) => {
                          if (hasChildren) {
                            e.preventDefault();
                            if (isOpen) toggleExpand(item.label);
                          }
                        }}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group',
                          active
                            ? 'bg-primary text-primary-foreground shadow-sm'
                            : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                          !isOpen && 'justify-center px-2'
                        )}
                      >
                        <item.icon className={cn('h-5 w-5 shrink-0', active && 'text-primary-foreground')} />
                        
                        <span
                          className={cn(
                            'flex-1 whitespace-nowrap overflow-hidden transition-all duration-300',
                            !isOpen && 'w-0 opacity-0'
                          )}
                        >
                          {item.label}
                        </span>

                        {item.badge && isOpen && (
                          <Badge variant={active ? 'secondary' : 'default'} className="ml-auto text-xs">
                            {item.badge}
                          </Badge>
                        )}

                        {hasChildren && isOpen && (
                          <ChevronLeft
                            className={cn(
                              'h-4 w-4 transition-transform duration-200',
                              isExpanded && '-rotate-90'
                            )}
                          />
                        )}
                      </Link>
                    </TooltipTrigger>
                    
                    {!isOpen && (
                      <TooltipContent side="right" className="flex items-center gap-4">
                        {item.label}
                        {item.badge && (
                          <Badge variant="default" className="text-xs">
                            {item.badge}
                          </Badge>
                        )}
                      </TooltipContent>
                    )}
                  </Tooltip>

                  {/* Submenu */}
                  {hasChildren && isOpen && isExpanded && (
                    <div className="mt-1 ml-4 pl-4 border-l border-border space-y-1 animate-slide-down">
                      {item.children?.filter(child => hasRole(child.roles)).map((child) => (
                        <Link
                          key={child.href}
                          href={child.href}
                          className={cn(
                            'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200',
                            isActive(child.href)
                              ? 'bg-primary/10 text-primary font-medium'
                              : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                          )}
                        >
                          <child.icon className="h-4 w-4" />
                          {child.label}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </nav>
        </ScrollArea>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-card">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                onClick={handleLogout}
                className={cn(
                  'w-full flex items-center gap-3 text-muted-foreground hover:text-destructive hover:bg-destructive/10',
                  !isOpen && 'justify-center px-2'
                )}
              >
                <LogOut className="h-5 w-5" />
                <span
                  className={cn(
                    'whitespace-nowrap overflow-hidden transition-all duration-300',
                    !isOpen && 'w-0 opacity-0'
                  )}
                >
                  Logout
                </span>
              </Button>
            </TooltipTrigger>
            {!isOpen && <TooltipContent side="right">Logout</TooltipContent>}
          </Tooltip>
        </div>

        {/* Mobile Overlay */}
        {isMobile && isOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-[-1]"
            onClick={onToggle}
          />
        )}
      </aside>
    </TooltipProvider>
  );
}
