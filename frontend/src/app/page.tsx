'use client';

import { Suspense, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { CheckCircle, AlertCircle, Clock, Link as LinkIcon, Save } from 'lucide-react';

function Dashboard() {
  const searchParams = useSearchParams();
  const success = searchParams.get('success');
  const error = searchParams.get('error');

  const [time, setTime] = useState('09:00');
  const [isSaving, setIsSaving] = useState(false);
  const [timeMsg, setTimeMsg] = useState('');

  // Remove URL params neatly after 5 seconds if success
  useEffect(() => {
    if (success) {
      setTimeout(() => {
        window.history.replaceState(null, '', '/');
      }, 5000);
    }
  }, [success]);

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

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-slate-900 p-8 text-center">
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold text-slate-900">
            BLC
          </div>
          <h1 className="text-2xl font-bold text-white">Automation Panel</h1>
          <p className="text-slate-400 mt-2">Daily LinkedIn Quotes Simplified</p>
        </div>

        <div className="p-8 space-y-6">
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-start gap-3">
              <CheckCircle className="w-5 h-5 mt-0.5 shrink-0" />
              <div>
                <h3 className="font-semibold">Successfully Connected!</h3>
                <p className="text-sm mt-1">Your LinkedIn account is now connected and automated.</p>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
              <div>
                <h3 className="font-semibold">Connection Failed</h3>
                <p className="text-sm mt-1">Please check your settings and try again. Error: {error}</p>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <h3 className="font-semibold text-slate-700 flex items-center gap-2 mb-2">
                <LinkIcon className="w-5 h-5 text-[#0A66C2]" />
                1. Connect LinkedIn
              </h3>
              <p className="text-sm text-slate-500 mb-4">Authorize the app to post daily quotes on your behalf.</p>
              <a
                href="/api/auth/linkedin"
                className="w-full flex items-center justify-center gap-2 bg-[#0A66C2] hover:bg-[#084e96] text-white py-3 px-4 rounded-lg font-medium transition-colors"
              >
                <LinkIcon className="w-5 h-5" />
                Connect with LinkedIn
              </a>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
              <h3 className="font-semibold text-slate-700 flex items-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-slate-600" />
                2. Set Post Time (IST)
              </h3>
              <p className="text-sm text-slate-500 mb-4">Choose what time the quote should be posted daily.</p>
              
              <div className="flex items-center gap-3">
                <input 
                  type="time" 
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="flex-1 border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-slate-400 font-medium text-slate-700" 
                />
                <button
                  onClick={handleSaveTime}
                  disabled={isSaving}
                  className="flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
              {timeMsg && (
                <p className={`text-sm mt-2 font-medium ${timeMsg.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
                  {timeMsg}
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
