'use client';

import React, { useState } from 'react';
import { UploadCloud, File, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

interface FileUploaderProps {
  onUploadComplete: (sessionId: string, filename: string) => void;
}

export default function FileUploader({ onUploadComplete }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    if (!file.name.match(/\.(csv|xlsx)$/)) {
      setError('Please upload a CSV or Excel file.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const response = await api.uploadFile(file);
      onUploadComplete(response.session_id, response.filename);
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto mt-10">
      <CardContent className="p-6">
        <div
          className={cn(
            "relative flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer transition-colors",
            isDragging ? "border-primary bg-primary/10" : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50",
            isUploading && "pointer-events-none opacity-50"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-upload')?.click()}
        >
          <input
            id="file-upload"
            type="file"
            className="hidden"
            accept=".csv,.xlsx"
            onChange={handleFileSelect}
            disabled={isUploading}
          />
          
          <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
            {isUploading ? (
              <>
                <Loader2 className="w-12 h-12 mb-4 text-primary animate-spin" />
                <p className="text-sm font-medium text-muted-foreground">
                  Processing dataset...
                </p>
              </>
            ) : (
              <>
                <UploadCloud className="w-12 h-12 mb-4 text-muted-foreground" />
                <p className="mb-2 text-sm font-semibold text-foreground">
                  Click to upload or drag and drop
                </p>
                <p className="text-xs text-muted-foreground">
                  CSV or Excel files (max 10MB)
                </p>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="flex items-center mt-4 p-3 text-sm text-destructive bg-destructive/10 rounded-md">
            <AlertCircle className="w-4 h-4 mr-2" />
            {error}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
