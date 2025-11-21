import { useState, useEffect, useRef, useCallback } from 'react';
import Head from 'next/head';
import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/router';
import { adminAPI, Stats, ScrapeJob } from '@/lib/api';
import { RefreshCw, Server, Database, Clock, ExternalLink, ArrowLeft, X, ChevronDown, LogOut } from 'lucide-react';
import Link from 'next/link';

interface LogEntry {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
}

export default function Admin() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [jobs, setJobs] = useState<ScrapeJob[]>([]);
  const [targetUrl, setTargetUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error'; text: string} | null>(null);
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, router]);

  useEffect(() => {
    if (status !== 'authenticated') return;
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  useEffect(() => {
    // Auto-scroll logs to bottom
    if (logsEndRef.current && showLogs) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, showLogs]);

  useEffect(() => {
    // Load logs when panel is shown
    if (showLogs) {
      loadLogs();
      const interval = setInterval(loadLogs, 2000); // Update logs every 2 seconds
      return () => clearInterval(interval);
    }
  }, [showLogs]);

  const loadLogs = async () => {
    try {
      const response = await fetch('/api/admin/logs?limit=100');
      const data = await response.json();
      setLogs(data.logs);
    } catch (error) {
      console.error('Failed to load logs:', error);
    }
  };

  const loadData = async () => {
    try {
      const [statsData, jobsData] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getJobs(10)
      ]);
      setStats(statsData);
      setJobs(jobsData);
      if (!targetUrl) {
        setTargetUrl(statsData.target_url);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const handleStartScrape = async () => {
    if (!targetUrl.trim()) {
      setMessage({ type: 'error', text: 'Please enter a valid URL' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      await adminAPI.startScrape({ target_url: targetUrl, reindex: true });
      setMessage({ type: 'success', text: 'Scraping job started successfully!' });
      loadData();
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to start scraping job'
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  // Show loading state while checking auth
  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <RefreshCw className="animate-spin h-8 w-8 text-primary-600 mx-auto" />
          <p className="mt-2 text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated (redirect will happen)
  if (status !== 'authenticated') {
    return null;
  }

  return (
    <>
      <Head>
        <title>Admin Panel - EchoChat</title>
      </Head>

      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
              <p className="text-sm text-gray-500">Connecté en tant que {session?.user?.email}</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => signOut({ callbackUrl: '/' })}
                className="flex items-center text-red-600 hover:text-red-700"
              >
                <LogOut size={20} className="mr-2" />
                Déconnexion
              </button>
              <Link
                href="/"
                className="flex items-center text-primary-600 hover:text-primary-700"
              >
                <ArrowLeft size={20} className="mr-2" />
                Back to Home
              </Link>
            </div>
          </div>

          {message && (
            <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
              {message.text}
            </div>
          )}

          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center mb-2">
                  <Database className="text-primary-600 mr-2" size={20} />
                  <p className="text-sm text-gray-600">Total Pages</p>
                </div>
                <p className="text-3xl font-bold text-gray-900">{stats.total_pages}</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center mb-2">
                  <Server className="text-primary-600 mr-2" size={20} />
                  <p className="text-sm text-gray-600">Total Chunks</p>
                </div>
                <p className="text-3xl font-bold text-gray-900">{stats.total_chunks}</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center mb-2">
                  <Clock className="text-primary-600 mr-2" size={20} />
                  <p className="text-sm text-gray-600">Frequency</p>
                </div>
                <p className="text-3xl font-bold text-gray-900">{stats.scrape_frequency_hours}h</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center mb-2">
                  <RefreshCw className="text-primary-600 mr-2" size={20} />
                  <p className="text-sm text-gray-600">Last Scrape</p>
                </div>
                <p className="text-sm font-medium text-gray-900">
                  {stats.last_scrape 
                    ? new Date(stats.last_scrape).toLocaleString() 
                    : 'Never'}
                </p>
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg shadow mb-8 p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Start New Scraping Job</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target URL
                </label>
                <input
                  type="url"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  placeholder="https://www.example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900"
                />
              </div>

              <button
                onClick={handleStartScrape}
                disabled={loading}
                className="w-full md:w-auto bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <RefreshCw className="animate-spin mr-2" size={18} />
                    Starting...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2" size={18} />
                    Start Scraping
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Recent Scraping Jobs</h2>
            
            {jobs.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No scraping jobs yet</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">ID</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">URL</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Pages</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map((job) => (
                      <tr key={job.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm text-gray-900">{job.id}</td>
                        <td className="py-3 px-4 text-sm">
                          <a 
                            href={job.target_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-primary-600 hover:underline flex items-center"
                          >
                            {job.target_url.substring(0, 40)}...
                            <ExternalLink size={14} className="ml-1" />
                          </a>
                        </td>
                        <td className="py-3 px-4">
                          <span className={"px-2 py-1 rounded text-xs font-medium " + getStatusBadge(job.status)}>
                            {job.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-900">{job.pages_scraped}</td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {new Date(job.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Logs Panel Button */}
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="fixed bottom-6 right-6 bg-primary-600 hover:bg-primary-700 text-white rounded-full p-4 shadow-lg transition hover:shadow-xl flex items-center gap-2"
            title="Toggle System Logs"
          >
            {showLogs ? <X size={24} /> : <ChevronDown size={24} />}
          </button>

          {/* Logs Modal */}
          {showLogs && (
            <div className="fixed inset-0 bg-black bg-opacity-50 z-40" onClick={() => setShowLogs(false)}>
              <div
                className="fixed bottom-0 right-0 w-full md:w-1/2 h-2/3 md:h-full bg-white shadow-2xl flex flex-col rounded-t-lg md:rounded-none overflow-hidden"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
                  <h3 className="font-semibold text-gray-900">System Logs</h3>
                  <button
                    onClick={() => setShowLogs(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <X size={20} />
                  </button>
                </div>

                {/* Logs Content */}
                <div className="flex-1 overflow-y-auto bg-gray-900 text-gray-100 font-mono text-sm p-4">
                  {logs.length === 0 ? (
                    <div className="text-gray-500 text-center py-8">No logs yet...</div>
                  ) : (
                    logs.map((log, index) => (
                      <div
                        key={index}
                        className={`py-1 ${
                          log.level === 'ERROR'
                            ? 'text-red-400'
                            : log.level === 'WARNING'
                            ? 'text-yellow-400'
                            : log.level === 'INFO'
                            ? 'text-green-400'
                            : 'text-gray-300'
                        }`}
                      >
                        <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                        <span className="font-semibold">{log.level}</span> {log.message}
                      </div>
                    ))
                  )}
                  <div ref={logsEndRef} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
