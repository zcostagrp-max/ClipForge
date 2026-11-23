'use client';

import { useState, useEffect, useRef } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';
const SAMPLE = 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4';

const DURATIONS = [10, 20, 30, 45, 60];
const QUALITIES = [
  { id: '720p', label: '720p' },
  { id: '1080p', label: '1080p Full HD' },
];

const DEMO_CLIPS = [
  { id: 'demo-1', title: 'Why most people stay broke', virality_score: 94, transcript: 'The real reason isn\'t what you think. Most people focus on the wrong things.', start: 124, end: 154, video_url: SAMPLE },
  { id: 'demo-2', title: 'The secret nobody talks about', virality_score: 87, transcript: 'Here\'s what actually works when everyone else is doing the opposite.', start: 312, end: 342, video_url: SAMPLE },
  { id: 'demo-3', title: 'This changed everything for me', virality_score: 91, transcript: 'I tried this for 30 days and the results were insane.', start: 45, end: 75, video_url: SAMPLE },
];

function ClipCard({ clip }: { clip: any }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [showPlayer, setShowPlayer] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const videoSrc = clip.video_url
    ? (clip.video_url.startsWith('http') ? clip.video_url : `${API_BASE}${clip.video_url}`)
    : null;

  const handlePreview = () => {
    setShowPlayer(true);
    setTimeout(() => {
      videoRef.current?.play().then(() => setPlaying(true)).catch(() => {});
    }, 100);
  };

  const handleDownload = async () => {
    if (!videoSrc) return;
    setDownloading(true);
    try {
      const res = await fetch(videoSrc);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(clip.title || 'clip').slice(0, 40)}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      window.open(videoSrc, '_blank');
    }
    setDownloading(false);
  };

  return (
    <div className="bg-zinc-900 rounded-2xl overflow-hidden border border-zinc-800">
      <div className="relative w-full aspect-[9/16] bg-zinc-800">
        {showPlayer && videoSrc ? (
          <video ref={videoRef} src={videoSrc} className="w-full h-full object-cover" controls playsInline crossOrigin="anonymous" onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)} />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-zinc-500 text-sm">Clip Preview</div>
        )}
        {!showPlayer && videoSrc && (
          <button onClick={handlePreview} className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition">
            <span className="w-14 h-14 rounded-full bg-white/90 flex items-center justify-center text-2xl">▶</span>
          </button>
        )}
      </div>
      <div className="p-4">
        <div className="flex justify-between items-start mb-2 gap-2">
          <h3 className="font-semibold line-clamp-2">{clip.title}</h3>
          <span className="text-orange-400 font-bold text-lg shrink-0">{clip.virality_score}</span>
        </div>
        <p className="text-xs text-zinc-500 mb-3 line-clamp-3">{clip.transcript}</p>
        <div className="flex gap-2">
          <button onClick={handlePreview} className="flex-1 text-center py-2 bg-zinc-800 rounded-lg text-sm hover:bg-zinc-700">{playing ? 'Playing' : 'Preview'}</button>
          <button onClick={handleDownload} disabled={downloading} className="flex-1 text-center py-2 bg-orange-500/20 text-orange-400 rounded-lg text-sm hover:bg-orange-500/30 disabled:opacity-50">{downloading ? 'Saving...' : 'Download'}</button>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [url, setUrl] = useState('');
  const [duration, setDuration] = useState(30);
  const [quality, setQuality] = useState('1080p');
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [demoMode, setDemoMode] = useState(!API_BASE);
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');

  useEffect(() => {
    if (!jobId || demoMode) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
        if (!res.ok) throw new Error('Failed');
        const data = await res.json();
        setJob(data);
        setProgress(data.progress || 0);
        setStage(data.stage || data.status);
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
        }
      } catch (e) {
        console.error(e);
        clearInterval(interval);
        setLoading(false);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId, demoMode]);

  const runDemo = () => {
    setLoading(true);
    setJob(null);
    setProgress(0);
    setStage('Downloading video');
    const stages = [
      { p: 15, s: 'Downloading video' },
      { p: 40, s: 'Transcribing audio' },
      { p: 65, s: 'AI finding best moments' },
      { p: 85, s: `Rendering ${duration}s clips (${quality})` },
      { p: 100, s: 'Done' },
    ];
    let i = 0;
    const timer = setInterval(() => {
      if (i < stages.length) {
        setProgress(stages[i].p);
        setStage(stages[i].s);
        i++;
      } else {
        clearInterval(timer);
        setJob({ status: 'completed', progress: 100, stage: 'Done', clips: DEMO_CLIPS });
        setLoading(false);
      }
    }, 700);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    if (demoMode || !API_BASE) { runDemo(); return; }
    setLoading(true);
    setJob(null);
    setProgress(0);
    setStage('Starting...');
    try {
      const res = await fetch(`${API_BASE}/api/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, target_duration: duration, quality }),
      });
      if (!res.ok) throw new Error('API error');
      const data = await res.json();
      setJobId(data.id);
      setJob(data);
    } catch (err) {
      console.error(err);
      setDemoMode(true);
      runDemo();
    }
  };

  const clips = job?.clips || [];

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <header className="text-center mb-10">
        <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-orange-400 to-pink-500 bg-clip-text text-transparent">ClipForge</h1>
        <p className="text-zinc-400 mt-3 text-lg">Paste a video URL → AI finds the best moments → download vertical clips</p>
        {demoMode && <p className="text-xs text-zinc-500 mt-2">Demo mode — set NEXT_PUBLIC_API_URL for real clipping</p>}
      </header>

      <form onSubmit={handleSubmit} className="mb-8 max-w-2xl mx-auto space-y-4">
        <div className="flex gap-3">
          <input type="url" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://youtube.com/watch?v=... or TikTok, Instagram, direct MP4" className="flex-1 px-4 py-3 rounded-xl bg-zinc-900 border border-zinc-800 focus:border-orange-500 outline-none text-white" required />
          <button type="submit" disabled={loading} className="px-6 py-3 rounded-xl bg-orange-500 hover:bg-orange-600 disabled:opacity-50 font-semibold transition">{loading ? 'Processing...' : 'Generate Clips'}</button>
        </div>
        <div className="flex flex-wrap gap-6 text-sm">
          <div>
            <span className="text-zinc-400 mr-2">Clip length:</span>
            {[10,20,30,45,60].map((d) => (
              <button key={d} type="button" onClick={() => setDuration(d)} className={`mr-1 px-3 py-1 rounded-lg ${duration === d ? 'bg-orange-500 text-white' : 'bg-zinc-800 text-zinc-300'}`}>{d}s</button>
            ))}
          </div>
          <div>
            <span className="text-zinc-400 mr-2">Quality:</span>
            {[{id:'720p',label:'720p'},{id:'1080p',label:'1080p Full HD'}].map((q) => (
              <button key={q.id} type="button" onClick={() => setQuality(q.id)} className={`mr-1 px-3 py-1 rounded-lg ${quality === q.id ? 'bg-orange-500 text-white' : 'bg-zinc-800 text-zinc-300'}`}>{q.label}</button>
            ))}
          </div>
        </div>
      </form>

      {(loading || progress > 0) && (
        <div className="mb-8 max-w-2xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-zinc-400">{stage || 'Working...'}</span>
            <span className="text-sm font-mono">{progress}%</span>
          </div>
          <div className="w-full bg-zinc-800 rounded-full h-2">
            <div className="bg-gradient-to-r from-orange-500 to-pink-500 h-2 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}

      {clips.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clips.map((clip: any) => <ClipCard key={clip.id} clip={clip} />)}
        </div>
      )}
    </div>
  );
}
