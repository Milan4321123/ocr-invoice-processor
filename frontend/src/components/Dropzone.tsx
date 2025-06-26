"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";

type UploadStatus = "idle" | "uploading" | "success" | "error";

interface DropzoneProps {
  onUploadComplete?: (data: any) => void;
  onUploadStart?: () => void;
  onUploadError?: (error: string) => void;
}

interface UploadResponse {
  id: string;
  url: string;
  status: string;
  filename: string;
  file_size: number;
  message: string;
}

export default function Dropzone({ onUploadComplete, onUploadStart, onUploadError }: DropzoneProps) {
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadedFile, setUploadedFile] = useState<UploadResponse | null>(null);
  
  const validateFilename = (filename: string): boolean => {
    const regex = /^\d{8}_[A-Z0-9]+_[A-Za-z]+_[A-Za-z]+\.pdf$/;
    return regex.test(filename);
  };
  
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  const onDrop = useCallback(async (files: File[]) => {
    if (files.length === 0) return;
    
    const pdf = files[0];
    
    // Reset previous state
    setErrorMessage("");
    setUploadedFile(null);
    setUploadProgress(0);
    
    // Validate file type
    if (pdf.type !== "application/pdf") {
      const errorMsg = "Nur PDF-Dateien sind erlaubt";
      setErrorMessage(errorMsg);
      setStatus("error");
      toast.error(errorMsg);
      onUploadError?.(errorMsg);
      return;
    }
    
    // Validate filename format
    if (!validateFilename(pdf.name)) {
      const errorMsg = "Dateiname muss dem Muster folgen: JJJJMMTT_KENNUNG_LIEFERANT_TYP.pdf";
      setErrorMessage(errorMsg);
      setStatus("error");
      toast.error("Ungültiges Dateinamen-Format");
      onUploadError?.(errorMsg);
      return;
    }
    
    setStatus("uploading");
    onUploadStart?.(); // Call the callback when upload starts
    
    try {
      const formData = new FormData();
      formData.append("file", pdf);
      
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/upload`, {
        method: "POST",
        body: formData,
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Upload fehlgeschlagen");
      }
      
      const data: UploadResponse = await response.json();
      setStatus("success");
      setUploadedFile(data);
      toast.success("Datei erfolgreich hochgeladen!");
      
      if (onUploadComplete) {
        onUploadComplete(data);
      }
    } catch (error) {
      console.error("Upload error:", error);
      const errorMsg = error instanceof Error ? error.message : "Upload fehlgeschlagen";
      setErrorMessage(errorMsg);
      setStatus("error");
      setUploadProgress(0);
      toast.error(errorMsg);
      onUploadError?.(errorMsg);
    }
  }, [onUploadComplete, onUploadStart, onUploadError]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    multiple: false
  });
  
  const resetUpload = () => {
    setStatus("idle");
    setErrorMessage("");
    setUploadedFile(null);
    setUploadProgress(0);
  };
  
  return (
    <div className="w-full">
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
          ${isDragActive ? 'bg-blue-50 border-blue-400 scale-105' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}
          ${status === 'error' ? 'border-red-300 bg-red-50' : ''}
          ${status === 'success' ? 'border-green-300 bg-green-50' : ''}
          ${status === 'uploading' ? 'border-blue-300 bg-blue-50' : ''}`}
      >
        <input {...getInputProps()} />
        
        {status === 'uploading' ? (
          <div className="text-blue-600">
            <svg className="animate-spin h-12 w-12 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-lg font-medium mb-2">Hochladen...</p>
            <div className="w-full bg-gray-200 rounded-full h-2 max-w-xs mx-auto">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="text-sm mt-2">{uploadProgress}%</p>
          </div>
        ) : status === 'success' ? (
          <div className="text-green-600">
            <svg className="h-12 w-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-lg font-medium mb-2">Upload erfolgreich!</p>
            {uploadedFile && (
              <div className="text-sm text-gray-600 mt-4">
                <p><strong>Datei:</strong> {uploadedFile.filename}</p>
                <p><strong>Größe:</strong> {formatFileSize(uploadedFile.file_size)}</p>
                <p><strong>Status:</strong> {uploadedFile.status}</p>
              </div>
            )}
            <button 
              onClick={(e) => {
                e.stopPropagation();
                resetUpload();
              }}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Weitere Datei hochladen
            </button>
          </div>
        ) : status === 'error' ? (
          <div className="text-red-600">
            <svg className="h-12 w-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-lg font-medium mb-2">Upload fehlgeschlagen</p>
            <p className="text-sm">{errorMessage}</p>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                resetUpload();
              }}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Erneut versuchen
            </button>
          </div>
        ) : (
          <div className="text-gray-500">
            <svg className="h-12 w-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-lg font-medium mb-2">
              {isDragActive ? 'PDF-Datei hier ablegen' : 'PDF-Datei per Drag & Drop hier ablegen'}
            </p>
            <p className="text-sm text-gray-400 mb-4">oder klicken Sie, um eine Datei auszuwählen</p>
            <div className="text-xs text-gray-400 bg-gray-100 rounded-lg p-3 max-w-md mx-auto">
              <p className="font-medium mb-1">Dateinamen-Anforderungen:</p>
              <p>JJJJMMTT_KENNUNG_LIEFERANT_TYP.pdf</p>
              <p className="mt-1">Beispiel: 20250528_INV001_ACME_SERVICE.pdf</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
