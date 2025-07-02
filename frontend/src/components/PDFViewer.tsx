'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { 
  ZoomIn, 
  ZoomOut, 
  RotateCw, 
  ChevronLeft, 
  ChevronRight,
  Maximize2,
  Minimize2,
  Download
} from 'lucide-react';

// Import CSS for react-pdf
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Set up PDF.js worker - using version compatible with our downgraded PDF.js
if (typeof window !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;
}

interface PDFViewerProps {
  pdfUrl: string;
  onLoadSuccess?: (numPages: number) => void;
  onLoadError?: (error: any) => void;
  className?: string;
}

export default function PDFViewer({ 
  pdfUrl, 
  onLoadSuccess, 
  onLoadError,
  className = "" 
}: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setPageNumber(1);
    setIsLoading(false);
    setError(null);
    onLoadSuccess?.(numPages);
  }, [onLoadSuccess]);

  const onDocumentLoadError = useCallback((error: any) => {
    console.error('PDF loading error:', error);
    console.error('PDF URL:', pdfUrl);
    console.error('Error details:', JSON.stringify(error, null, 2));
    setError(`Failed to load PDF: ${error.message || error.toString()}`);
    setIsLoading(false);
    onLoadError?.(error);
  }, [onLoadError, pdfUrl]);

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.25, 3.0));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handlePrevPage = () => {
    setPageNumber(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setPageNumber(prev => Math.min(prev + 1, numPages));
  };

  const handlePageInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const page = parseInt(e.target.value);
    if (page >= 1 && page <= numPages) {
      setPageNumber(page);
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = 'invoice.pdf';
    link.click();
  };

  const containerClasses = `
    ${className}
    ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : 'relative'}
    flex flex-col h-full
  `;

  return (
    <div className={containerClasses}>
      {/* PDF Controls Toolbar */}
      <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
        {/* Left side controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title="Zoom Out"
            disabled={scale <= 0.5}
          >
            <ZoomOut size={18} />
          </button>
          
          <span className="text-sm text-gray-600 min-w-[60px] text-center">
            {Math.round(scale * 100)}%
          </span>
          
          <button
            onClick={handleZoomIn}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title="Zoom In"
            disabled={scale >= 3.0}
          >
            <ZoomIn size={18} />
          </button>

          <div className="h-6 w-px bg-gray-300 mx-2" />

          <button
            onClick={handleRotate}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title="Rotate"
          >
            <RotateCw size={18} />
          </button>
        </div>

        {/* Center - Page Navigation */}
        {numPages > 0 && (
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrevPage}
              disabled={pageNumber <= 1}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Previous Page"
            >
              <ChevronLeft size={18} />
            </button>

            <div className="flex items-center space-x-1">
              <input
                type="number"
                value={pageNumber}
                onChange={handlePageInputChange}
                className="w-12 px-2 py-1 text-sm text-center border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                min={1}
                max={numPages}
              />
              <span className="text-sm text-gray-600">/ {numPages}</span>
            </div>

            <button
              onClick={handleNextPage}
              disabled={pageNumber >= numPages}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Next Page"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        )}

        {/* Right side controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleDownload}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title="Download PDF"
          >
            <Download size={18} />
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
        </div>
      </div>

      {/* PDF Content Area */}
      <div className="flex-1 overflow-auto bg-gray-100 p-4">
        <div className="flex justify-center">
          {error ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
              <div className="text-lg font-medium mb-2">Unable to load PDF</div>
              <div className="text-sm">{error}</div>
            </div>
          ) : (
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={
                <div className="flex items-center justify-center h-64">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              }
              className="shadow-lg"
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                rotate={rotation}
                loading={
                  <div className="flex items-center justify-center h-64 bg-white border border-gray-200 rounded">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                }
                className="border border-gray-300 bg-white"
              />
            </Document>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <div className="px-3 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
        {isLoading ? (
          'Loading PDF...'
        ) : error ? (
          'Error loading PDF'
        ) : (
          `Page ${pageNumber} of ${numPages} • ${Math.round(scale * 100)}% zoom`
        )}
      </div>
    </div>
  );
}
