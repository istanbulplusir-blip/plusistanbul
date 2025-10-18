'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import {
  DocumentTextIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  PrinterIcon,
  FunnelIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface Report {
  id: string;
  title: string;
  description: string;
  type: 'commission' | 'booking' | 'customer' | 'financial' | 'performance';
  status: 'ready' | 'generating' | 'failed';
  created_at: string;
  period: {
    start: string;
    end: string;
  };
  file_size?: string;
  download_count: number;
}

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  category: string;
}

interface DateRange {
  start: string;
  end: string;
  label: string;
}

export default function AgentReportsPage() {
  const t = useTranslations('agent');
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
  } = useAgent();

  // State for reports
  const [reports, setReports] = useState<Report[]>([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
    label: 'آخرین 30 روز'
  });
  const [generatingReport, setGeneratingReport] = useState(false);

  // Report templates
  const reportTemplates: ReportTemplate[] = [
    {
      id: 'commission_summary',
      name: t('reports.templates.commissionSummary'),
      description: t('reports.templates.commissionSummaryDesc'),
      icon: CurrencyDollarIcon,
      category: 'commission'
    },
    {
      id: 'booking_report',
      name: t('reports.templates.bookingReport'),
      description: t('reports.templates.bookingReportDesc'),
      icon: CalendarDaysIcon,
      category: 'booking'
    },
    {
      id: 'customer_report',
      name: t('reports.templates.customerReport'),
      description: t('reports.templates.customerReportDesc'),
      icon: UserGroupIcon,
      category: 'customer'
    },
    {
      id: 'financial_report',
      name: t('reports.templates.financialReport'),
      description: t('reports.templates.financialReportDesc'),
      icon: ChartBarIcon,
      category: 'financial'
    },
    {
      id: 'performance_report',
      name: t('reports.templates.performanceReport'),
      description: t('reports.templates.performanceReportDesc'),
      icon: ChartBarIcon,
      category: 'performance'
    }
  ];

  // Date range options
  const dateRanges: DateRange[] = [
    {
      start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین 7 روز'
    },
    {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین 30 روز'
    },
    {
      start: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین 90 روز'
    },
    {
      start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
      label: 'آخرین سال'
    }
  ];

  // Load reports
  const loadReports = async () => {
    setLoadingReports(true);
    try {
      // Mock reports data
      const mockReports: Report[] = [
        {
          id: '1',
          title: 'گزارش کمیسیون - دی 1402',
          description: 'گزارش کامل کمیسیون‌های دریافتی در ماه دی',
          type: 'commission',
          status: 'ready',
          created_at: '2024-01-15T10:30:00Z',
          period: {
            start: '2023-12-22',
            end: '2024-01-20'
          },
          file_size: '2.3 MB',
          download_count: 5
        },
        {
          id: '2',
          title: 'گزارش سفارشات - آذر 1402',
          description: 'گزارش تمام سفارشات ثبت شده در ماه آذر',
          type: 'booking',
          status: 'ready',
          created_at: '2023-12-15T14:20:00Z',
          period: {
            start: '2023-11-22',
            end: '2023-12-21'
          },
          file_size: '1.8 MB',
          download_count: 3
        },
        {
          id: '3',
          title: 'گزارش مشتریان - آبان 1402',
          description: 'گزارش تحلیل مشتریان و رفتار خرید',
          type: 'customer',
          status: 'ready',
          created_at: '2023-11-15T09:15:00Z',
          period: {
            start: '2023-10-23',
            end: '2023-11-21'
          },
          file_size: '3.1 MB',
          download_count: 2
        },
        {
          id: '4',
          title: 'گزارش مالی - مهر 1402',
          description: 'گزارش مالی کامل درآمد و هزینه‌ها',
          type: 'financial',
          status: 'generating',
          created_at: '2023-10-15T16:45:00Z',
          period: {
            start: '2023-09-23',
            end: '2023-10-22'
          },
          download_count: 0
        }
      ];
      
      setReports(mockReports);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoadingReports(false);
    }
  };

  // Generate new report
  const generateReport = async () => {
    if (!selectedTemplate) {
      alert(t('reports.selectTemplate'));
      return;
    }

    setGeneratingReport(true);
    try {
      // Mock report generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newReport: Report = {
        id: Date.now().toString(),
        title: `${reportTemplates.find(t => t.id === selectedTemplate)?.name} - ${selectedDateRange.label}`,
        description: `گزارش ${reportTemplates.find(t => t.id === selectedTemplate)?.name} برای دوره ${selectedDateRange.label}`,
        type: (reportTemplates.find(t => t.id === selectedTemplate)?.category as 'customer' | 'commission' | 'performance' | 'booking' | 'financial') || 'commission',
        status: 'ready',
        created_at: new Date().toISOString(),
        period: {
          start: selectedDateRange.start,
          end: selectedDateRange.end
        },
        file_size: '1.5 MB',
        download_count: 0
      };
      
      setReports(prev => [newReport, ...prev]);
      setSelectedTemplate('');
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setGeneratingReport(false);
    }
  };

  // Download report
  const downloadReport = (reportId: string) => {
    // Mock download functionality
    alert(`Downloading report ${reportId}...`);
  };

  // View report
  const viewReport = (reportId: string) => {
    // Mock view functionality
    alert(`Viewing report ${reportId}...`);
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'generating':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      case 'failed':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  // Get status text
  const getStatusText = (status: string) => {
    switch (status) {
      case 'ready':
        return t('reports.status.ready');
      case 'generating':
        return t('reports.status.generating');
      case 'failed':
        return t('reports.status.failed');
      default:
        return status;
    }
  };

  // Get type icon
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'commission':
        return <CurrencyDollarIcon className="w-5 h-5 text-green-600" />;
      case 'booking':
        return <CalendarDaysIcon className="w-5 h-5 text-blue-600" />;
      case 'customer':
        return <UserGroupIcon className="w-5 h-5 text-purple-600" />;
      case 'financial':
        return <ChartBarIcon className="w-5 h-5 text-orange-600" />;
      case 'performance':
        return <ChartBarIcon className="w-5 h-5 text-indigo-600" />;
      default:
        return <DocumentTextIcon className="w-5 h-5 text-gray-600" />;
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(locale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Load reports on component mount
  useEffect(() => {
    loadReports();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t('reports.title')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t('reports.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Generate Report */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 sticky top-8">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                {t('reports.generateNew')}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('reports.selectTemplate')}
                  </label>
                  <select
                    value={selectedTemplate}
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="">{t('reports.chooseTemplate')}</option>
                    {reportTemplates.map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {t('reports.dateRange')}
                  </label>
                  <select
                    value={selectedDateRange.label}
                    onChange={(e) => {
                      const range = dateRanges.find(r => r.label === e.target.value);
                      if (range) setSelectedDateRange(range);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {dateRanges.map((range) => (
                      <option key={range.label} value={range.label}>
                        {range.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <button
                  onClick={generateReport}
                  disabled={!selectedTemplate || generatingReport}
                  className={cn(
                    "w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed",
                    isRTL ? "space-x-reverse space-x-2" : "space-x-2"
                  )}
                >
                  {generatingReport ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>{t('reports.generating')}</span>
                    </>
                  ) : (
                    <>
                      <DocumentTextIcon className="w-4 h-4" />
                      <span>{t('reports.generate')}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Reports List */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    {t('reports.recentReports')}
                  </h3>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={loadReports}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                    >
                      <FunnelIcon className="w-4 h-4 mr-2" />
                      {t('reports.refresh')}
                    </button>
                  </div>
                </div>

                {loadingReports ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-3 text-gray-600 dark:text-gray-400">
                      {t('reports.loading')}
                    </span>
                  </div>
                ) : reports.length === 0 ? (
                  <div className="text-center py-12">
                    <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="mt-2 text-gray-600 dark:text-gray-400">
                      {t('reports.noReports')}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {reports.map((report) => (
                      <div key={report.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3">
                            {getTypeIcon(report.type)}
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {report.title}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {report.description}
                              </p>
                              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-500">
                                <span>
                                  {formatDate(report.created_at)}
                                </span>
                                <span>
                                  {report.period.start} - {report.period.end}
                                </span>
                                {report.file_size && (
                                  <span>
                                    {report.file_size}
                                  </span>
                                )}
                                <span>
                                  {report.download_count} {t('reports.downloads')}
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <div className="flex items-center space-x-1">
                              {getStatusIcon(report.status)}
                              <span className="text-sm text-gray-600 dark:text-gray-400">
                                {getStatusText(report.status)}
                              </span>
                            </div>
                            
                            {report.status === 'ready' && (
                              <div className="flex items-center space-x-1">
                                <button
                                  onClick={() => viewReport(report.id)}
                                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                  title={t('reports.view')}
                                >
                                  <EyeIcon className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => downloadReport(report.id)}
                                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                  title={t('reports.download')}
                                >
                                  <ArrowDownTrayIcon className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => window.print()}
                                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                  title={t('reports.print')}
                                >
                                  <PrinterIcon className="w-4 h-4" />
                                </button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Report Templates */}
        <div className="mt-8">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {t('reports.availableTemplates')}
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reportTemplates.map((template) => (
                <div key={template.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <template.icon className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {template.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {template.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
