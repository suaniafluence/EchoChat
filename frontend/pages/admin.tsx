import { useState, useEffect } from 'react';
import Head from 'next/head';
import { adminAPI, Stats, ScrapeJob } from '@/lib/api';
import { RefreshCw, Server, Database, Clock, ExternalLink, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function Admin() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [jobs, setJobs] = useState<ScrapeJob[]>([]);
  const [targetUrl, setTargetUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error'; text: string} | null>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

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

  return (
    <>
      <Head>
        <title>Admin Panel - EchoChat</title>
      </Head>

      <div className="min-h-screen bg-gray-50 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
            <Link 
              href="/"
              className="flex items-center text-primary-600 hover:text-primary-700"
            >
              <ArrowLeft size={20} className="mr-2" />
              Back to Home
            </Link>
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
        </div>
      </div>
    </>
  );
}
