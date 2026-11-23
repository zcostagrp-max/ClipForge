'use client';

import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [url, setUrl] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!jobId) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
        const data = await res.json();
        setJob(data);
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
        }
      } catch (e) {
        console.error(e);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setJob(null);
    try {
      const res = await fetch(`${API_BASE}/api/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      setJobId(data.id);
      setJob(data);
    } catch (err) {
      alert('Failed to start job');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-orange-400 to-pink-500 bg-clip-text text-transparent">
          ClipForge
        </h1>
        <p className="text-zinc-400 mt-3 text-lg">Paste any video URL → get viral short clips with captions</p>
      </header>

      <form onSubmit={handleSubmit} className="mb-10">
        <div className="flex gap-3 max-w-2xl mx-auto">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=... or TikTok, Instagram, direct MP4"
            className="flex-1 px-4 py-3 rounded-xl bg-zinc-900 border border-zinc-800 focus:border-orange-500 outline-none"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-orange-500 hover:bg-orange-600 disabled:opacity-50 font-semibold transition"
          >
            {loading ? 'Processing...' : 'Generate Clips'}
          </button>
        </div>
      </form>

      {job && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-zinc-400">{job.stage || job.status}</span>
            <span className="text-sm font-mono">{job.progress}%</span>
          </div>
          <div className="w-full bg-zinc-800 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-orange-500 to-pink-500 h-2 rounded-full transition-all"
              style={{ width: `${job.progress}%` }}
            />
          </div>
          {job.error && <p className="text-red-400 text-sm mt-2">{job.error}</p>}
        </div>
      )}

      {job?.clips?.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {job.clips.map((clip: any) => (
            <div key={clip.id} className="bg-zinc-900 rounded-2xl overflow-hidden border border-zinc-800">
              {clip.thumbnail_url && (
                <img
                  src={`${API_BASE}${clip.thumbnail_url}`}
                  alt={clip.title}
                  className="w-full aspect-[9/16] object-cover"
                />
              )}
              <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold line-clamp-2">{clip.title}</h3>
                  <span className="text-orange-400 font-bold text-lg">{clip.virality_score}</span>
                </div>
                <p className="text-xs text-zinc-500 mb-3 line-clamp-2">{clip.transcript}</p>
                <div className="flex gap-2">
                  {clip.video_url && (
                    <a
                      href={`${API_BASE}${clip.video_url}`}
                      target="_blank"
                      className="flex-1 text-center py-2 bg-zinc-800 rounded-lg text-sm hover:bg-zinc-700"
                    >
                      Preview
                    </a>
                  )}
                  <a
                    href={`${API_BASE}/api/clips/${clip.id}/download`}
                    className="flex-1 text-center py-2 bg-orange-500/20 text-orange-400 rounded-lg text-sm hover:bg-orange-500/30"
                  >
                    Download
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
