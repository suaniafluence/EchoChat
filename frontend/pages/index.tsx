import { useEffect, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Chat from '@/components/Chat';
import { adminAPI } from '@/lib/api';
import { AlertCircle } from 'lucide-react';

export default function Home() {
  const [homepage, setHomepage] = useState<{html: string; title: string; url?: string} | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Sanitize HTML to prevent XSS attacks and add base tag for resource loading
  const sanitizeHTML = (html: string, baseUrl: string): string => {
    // Remove script tags, event handlers, and javascript: protocols
    let sanitized = html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
      .replace(/on\w+\s*=\s*[^\s>]*/gi, '')
      .replace(/javascript:/gi, '');

    // Add base tag to ensure resources load from original domain
    // Extract the base URL (protocol + domain)
    const urlMatch = baseUrl.match(/^(https?:\/\/[^\/]+)/);
    if (urlMatch) {
      const base = urlMatch[1];
      // Insert base tag after <head> tag
      sanitized = sanitized.replace(/<head>/i, `<head><base href="${base}/" target="_parent">`);
      // If no head tag, insert at the beginning
      if (!sanitized.includes('<base')) {
        sanitized = `<base href="${base}/" target="_parent">` + sanitized;
      }
    }

    return sanitized;
  };

  useEffect(() => {
    loadHomepage();
  }, []);

  const loadHomepage = async () => {
    try {
      setLoading(true);
      const data = await adminAPI.getHomepage();
      setHomepage({ html: data.html, title: data.title, url: data.url });
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
            Please visit the <Link href="/admin" className="text-primary-600 hover:underline">admin panel</Link> to
            start scraping a website.
          </p>
          <Link
            href="/admin"
            className="block w-full text-center bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded transition"
          >
            Go to Admin Panel
          </Link>
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
        {/* Demo disclaimer banner */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 text-center shadow-md">
          <p className="text-sm md:text-base font-medium">
            <strong>Démo technique</strong> — Contenu issu d'un site externe. Ce n'est pas une copie ni un site pirate.
          </p>
          <p className="text-xs md:text-sm opacity-90 mt-1">
            EchoChat charge uniquement la page publique sélectionnée et y ajoute un assistant conversationnel pour illustrer le fonctionnement d'un RAG (Recherche Augmentée par Génération). Aucune donnée privée n'est collectée, rien n'est hébergé définitivement. Démonstration pédagogique uniquement.
          </p>
        </div>
        {homepage && (
          <iframe
            srcDoc={sanitizeHTML(homepage.html, homepage.url || '')}
            className="w-full min-h-screen border-0"
            title={homepage.title}
            sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox"
            style={{
              width: '100%',
              height: 'calc(100vh - 80px)',
              border: 'none',
              display: 'block'
            }}
          />
        )}
        <Chat />
      </main>
    </>
  );
}
