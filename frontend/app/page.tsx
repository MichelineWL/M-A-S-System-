'use client';

import React, { useState } from 'react';
import { Bot, Sparkles } from 'lucide-react';
import FileUploader from '@/components/FileUploader';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string | null>(null);

  const handleUploadComplete = (sid: string, fname: string) => {
    setSessionId(sid);
    setFilename(fname);
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-4 md:p-8 bg-background text-foreground font-sans">
      {/* Header */}
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex mb-8">
        <div className="fixed left-0 top-0 flex w-full justify-center border-b border-border bg-background/80 backdrop-blur-md pb-6 pt-6 dark:border-neutral-800 dark:bg-zinc-800/30 lg:static lg:w-auto lg:rounded-xl lg:border lg:bg-zinc-200 lg:p-4 lg:dark:bg-zinc-900/30">
          <div className="flex items-center gap-2 font-bold text-lg">
            <Sparkles className="w-5 h-5 text-primary" />
            <span>Intelligent Data Room</span>
          </div>
        </div>
        <div className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-background via-background dark:from-black dark:via-black lg:static lg:h-auto lg:w-auto lg:bg-none">
          {sessionId && (
            <div className="flex items-center gap-2 px-4 py-2 bg-secondary rounded-full text-xs font-mono">
              <span className="text-muted-foreground">Analyzing:</span>
              <span className="font-semibold text-primary truncate max-w-[200px]">{filename}</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 w-full max-w-5xl flex flex-col items-center justify-center">
        {!sessionId ? (
          <div className="w-full max-w-2xl animate-in fade-in slide-in-from-bottom-5 duration-700">
            <div className="text-center mb-10 space-y-4">
              <div className="inline-block p-4 rounded-full bg-secondary mb-4">
                <Bot className="w-12 h-12 text-primary" />
              </div>
              <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">
                Talk to your Data
              </h1>
              <p className="mx-auto max-w-[700px] text-gray-400 md:text-xl">
                Upload your dataset and let our Multi-Agent AI analyze, visualize, and find insights for you instantly.
              </p>
            </div>
            
            <FileUploader onUploadComplete={handleUploadComplete} />
          </div>
        ) : (
          <div className="w-full h-full animate-in fade-in zoom-in-95 duration-500">
            <ChatInterface sessionId={sessionId} />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="w-full text-center text-xs text-muted-foreground mt-8 pb-4">
        Powered by Google Gemini 2.5 Flash & PandasAI
      </div>
    </main>
  );
}
