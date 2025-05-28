"use client";

import { useState } from "react";
import Dropzone from "../../components/Dropzone";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function UploadPage() {
  const router = useRouter();
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  
  const handleUploadComplete = (data: any) => {
    setUploadSuccess(true);
    setUploadedFiles(prev => [...prev, data]);
    
    // Auto-redirect to dashboard after 3 seconds
    setTimeout(() => {
      router.push('/dashboard');
    }, 3000);
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Invoice</h1>
          <p className="text-gray-600">
            Upload your PDF invoices for OCR processing. Make sure the filename follows the required format.
          </p>
        </div>
        
        {/* Upload Area */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <Dropzone onUploadComplete={handleUploadComplete} />
        </div>
        
        {/* Upload Success Summary */}
        {uploadedFiles.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-medium text-green-800 mb-3">
              Recently Uploaded Files
            </h3>
            <div className="space-y-2">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="flex items-center justify-between bg-white p-3 rounded border border-green-200">
                  <div>
                    <p className="font-medium text-gray-900">{file.filename}</p>
                    <p className="text-sm text-gray-500">Status: {file.status}</p>
                  </div>
                  <a 
                    href={file.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View PDF
                  </a>
                </div>
              ))}
            </div>
            {uploadSuccess && (
              <p className="text-sm text-green-600 mt-3">
                Redirecting to dashboard in 3 seconds...
              </p>
            )}
          </div>
        )}
        
        {/* Navigation */}
        <div className="flex justify-between items-center">
          <Link 
            href="/" 
            className="text-gray-600 hover:text-gray-900 font-medium flex items-center"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Home
          </Link>
          
          <Link 
            href="/dashboard" 
            className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-lg font-medium flex items-center"
          >
            View Dashboard
            <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
        
        {/* Filename Format Help */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-800 mb-3">
            Filename Format Requirements
          </h3>
          <div className="text-sm text-blue-700">
            <p className="mb-2">Your PDF filename must follow this exact pattern:</p>
            <code className="bg-blue-100 px-2 py-1 rounded font-mono">
              YYYYMMDD_IDENTIFIER_VENDOR_TYPE.pdf
            </code>
            
            <div className="mt-4 space-y-2">
              <p><strong>YYYYMMDD:</strong> Date in format (e.g., 20250528)</p>
              <p><strong>IDENTIFIER:</strong> Alphanumeric ID (e.g., INV001, REF123)</p>
              <p><strong>VENDOR:</strong> Vendor name in letters (e.g., ACME, Google)</p>
              <p><strong>TYPE:</strong> Document type in letters (e.g., SERVICE, PRODUCT)</p>
            </div>
            
            <div className="mt-4">
              <p className="font-medium">Valid examples:</p>
              <ul className="list-disc list-inside mt-1 space-y-1">
                <li><code>20250528_INV001_ACME_SERVICE.pdf</code></li>
                <li><code>20250527_REF123_Google_PRODUCT.pdf</code></li>
                <li><code>20250526_ORD456_Microsoft_LICENSE.pdf</code></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
