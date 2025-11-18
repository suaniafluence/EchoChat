import { useEffect, useState } from 'react';
import Head from 'next/head';
import Chat from '@/components/Chat';
import { adminAPI } from '@/lib/api';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const [homepage, setHomepage] = useState<{html: string; title: string} | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sanitize HTML to prevent XSS attacks
  const sanitizeHTML = (html: string): string => {
    // Remove script tags, event handlers, and javascript: protocols
    return html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
      .replace(/on\w+\s*=\s*[^\s>]*/gi, '')
      .replace(/javascript:/gi, '');
  };

  useEffect(() => {
    loadHomepage();
  }, []);

  const loadHomepage = async () => {
    try {
      setLoading(true);
      const data = await adminAPI.getHomepage();
      setHomepage({ html: data.html, title: data.title });
      setError(null);
    } catch (err: any) {
      console.error('Failed to load homepage:', err);
      setError(err.response?.data?.detail || 'Failed to load homepage');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading homepage...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-4">
            <AlertCircle className="text-red-500 mr-2" size={24} />
            <h2 className="text-xl font-semibold text-gray-900">No Homepage Found</h2>
          </div>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500 mb-4">
            Please visit the <a href="/admin" className="text-primary-600 hover:underline">admin panel</a> to
            start scraping a website.
          </p>
          <a
            href="/admin"
            className="block w-full text-center bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded transition"
          >
            Go to Admin Panel
          </a>
        </div>
        <Chat />
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{homepage?.title || 'EchoChat'}</title>
        <meta name="description" content="EchoChat - AI-powered website assistant" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="min-h-screen">
        {homepage && (
          <div
            dangerouslySetInnerHTML={{ __html: sanitizeHTML(homepage.html) }}
            className="w-full"
          />
        )}
        <Chat />
      </main>
    </>
  );
}
