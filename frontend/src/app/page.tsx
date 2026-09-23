'use client';

import { Suspense, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { CheckCircle, AlertCircle, Clock, Link as LinkIcon, Save, Send } from 'lucide-react';

function Dashboard() {
  const searchParams = useSearchParams();
  const success = searchParams.get('success');
  const error = searchParams.get('error');
  const fallbackToken = searchParams.get('token');
  const fallbackUrn = searchParams.get('urn');
  const [copied, setCopied] = useState(false);

  const [time, setTime] = useState('18:30');
  const [isSaving, setIsSaving] = useState(false);
  const [timeMsg, setTimeMsg] = useState('');

  const [isPosting, setIsPosting] = useState(false);
  const [postMsg, setPostMsg] = useState('');

  // Remove URL params neatly after 5 seconds if success
  useEffect(() => {
    if (success) {
      setTimeout(() => {
        window.history.replaceState(null, '', '/');
      }, 5000);
    }
  }, [success]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  const handleSaveTime = async () => {
    setIsSaving(true);
    setTimeMsg('');
    try {
      const res = await fetch('/api/github/time', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ time }),
      });
      const data = await res.json();
      if (res.ok) {
        setTimeMsg('Time updated successfully!');
      } else {
        setTimeMsg(data.error || 'Failed to update time');
      }
    } catch (err) {
      setTimeMsg('Failed to update time');
    }
    setIsSaving(false);
  };

  const handlePostNow = async () => {
    setIsPosting(true);
    setPostMsg('');
    try {
      const res = await fetch('/api/github/post', { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setPostMsg('Post triggered! Check LinkedIn in 1 minute.');
      } else {
        setPostMsg(data.error || 'Failed to trigger post');
      }
    } catch (err) {
      setPostMsg('Failed to trigger post');
    }
    setIsPosting(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden flex flex-col max-h-[90vh]">
        
        <div className="bg-slate-900 p-6 text-center shrink-0">
          <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-3 text-xl font-bold text-slate-900">
            BLC
          </div>
          <h1 className="text-xl font-bold text-white">Automation Panel</h1>
          <p className="text-slate-400 mt-1 text-sm">Daily LinkedIn Quotes Simplified</p>
        </div>

        <div className="p-6 space-y-5 overflow-y-auto">
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-start gap-3">
              <CheckCircle className="w-5 h-5 mt-0.5 shrink-0" />
              <div>
                <h3 className="font-semibold text-sm">Successfully Connected!</h3>
                <p className="text-xs mt-1">Your LinkedIn account is now connected and automated.</p>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-amber-50 border border-amber-200 text-amber-900 p-4 rounded-lg flex flex-col gap-2">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 mt-0.5 shrink-0 text-amber-600" />
                <div>
                  <h3 className="font-semibold text-sm">GitHub Secret Auto-Save Notice</h3>
                  <p className="text-xs mt-1 text-amber-700">
                    LinkedIn authentication was successful! However, your <code>GITHUB_PAT</code> needs <code>repo</code> permissions to auto-save secrets into GitHub.
                  </p>
                </div>
              </div>
              {fallbackToken && (
                <div className="mt-2 pt-2 border-t border-amber-200">
                  <p className="text-xs font-medium text-amber-800 mb-1">Generated LinkedIn Access Token:</p>
                  <div className="flex items-center gap-2">
                    <input
                      type="password"
                      readOnly
                      value={fallbackToken}
                      className="flex-1 bg-white border border-amber-300 rounded px-2 py-1 text-xs text-slate-700 font-mono"
                    />
                    <button
                      onClick={() => copyToClipboard(fallbackToken)}
                      className="bg-amber-700 hover:bg-amber-800 text-white text-xs px-3 py-1 rounded font-medium transition-colors"
                    >
                      {copied ? 'Copied!' : 'Copy Token'}
                    </button>
                  </div>
                  <p className="text-[11px] text-amber-700 mt-1.5">
                    💡 Paste this token into GitHub Repo &rarr; Settings &rarr; Secrets &rarr; <code>LINKEDIN_ACCESS_TOKEN</code>.
                  </p>
                </div>
              )}
            </div>
          )}

          <div className="space-y-4">
            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200">
              <h3 className="font-semibold text-emerald-800 text-sm flex items-center gap-2 mb-1">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                1. LinkedIn Account Status
              </h3>
              <p className="text-xs text-emerald-700 font-medium">
                Connected via Buffer API &rarr; Bulk Leads Caller Page
              </p>
              <div className="mt-2.5 flex items-center gap-1.5 text-[11px] text-emerald-800 font-semibold bg-emerald-100/80 px-2.5 py-1 rounded-md w-fit">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Active &amp; Ready for Daily Post
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <h3 className="font-semibold text-slate-700 text-sm flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-slate-600" />
                2. Set Post Time (IST)
              </h3>
              <p className="text-xs text-slate-500 mb-3">Choose what time the quote should be posted daily.</p>
              
              <div className="flex items-center gap-3">
                <input 
                  type="time" 
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="flex-1 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-slate-400 font-medium text-slate-700" 
                />
                <button
                  onClick={handleSaveTime}
                  disabled={isSaving}
                  className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white py-2 px-4 rounded-lg font-medium text-sm transition-colors"
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
              {timeMsg && (
                <p className={`text-xs mt-2 font-medium ${timeMsg.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
                  {timeMsg}
                </p>
              )}
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <h3 className="font-semibold text-slate-700 text-sm flex items-center gap-2 mb-2">
                <Send className="w-4 h-4 text-emerald-600" />
                3. Test Post (Manual)
              </h3>
              <p className="text-xs text-slate-500 mb-4">Click below to bypass the timer and post a quote immediately.</p>
              <button
                onClick={handlePostNow}
                disabled={isPosting}
                className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white py-2.5 px-4 rounded-lg font-medium text-sm transition-colors"
              >
                <Send className="w-4 h-4" />
                {isPosting ? 'Triggering Post...' : 'Post Now (Test)'}
              </button>
              {postMsg && (
                <p className={`text-xs mt-2 font-medium text-center ${postMsg.includes('Check') ? 'text-green-600' : 'text-red-600'}`}>
                  {postMsg}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <Suspense fallback={<div className="p-8 text-center">Loading...</div>}>
      <Dashboard />
    </Suspense>
  );
}
