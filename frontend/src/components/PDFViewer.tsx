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
  Download,
  X,
  ArrowLeft
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
  const [showToolbar, setShowToolbar] = useState<boolean>(false);
  const [scrollContainer, setScrollContainer] = useState<HTMLDivElement | null>(null);

  // Handle scroll to show/hide toolbar
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.target as HTMLDivElement;
    const { scrollTop, scrollHeight, clientHeight } = target;
    const isNearBottom = scrollTop + clientHeight >= scrollHeight - 50; // 50px threshold
    setShowToolbar(isNearBottom);
  };

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

  // Keyboard shortcuts for better UX
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only handle shortcuts when PDF viewer is focused or in fullscreen
      if (!isFullscreen && document.activeElement?.closest('.pdf-viewer-container') === null) {
        return;
      }

      switch (e.key) {
        case 'ArrowLeft':
          e.preventDefault();
          handlePrevPage();
          break;
        case 'ArrowRight':
          e.preventDefault();
          handleNextPage();
          break;
        case '+':
        case '=':
          e.preventDefault();
          handleZoomIn();
          break;
        case '-':
          e.preventDefault();
          handleZoomOut();
          break;
        case 'Escape':
          if (isFullscreen) {
            e.preventDefault();
            setIsFullscreen(false);
          }
          break;
        case 'f':
        case 'F':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            toggleFullscreen();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen, pageNumber, numPages, scale]);

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
    // Reset zoom when entering/exiting fullscreen for better UX
    if (!isFullscreen) {
      setScale(1.0);
    }
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = 'invoice.pdf';
    link.click();
  };

  const containerClasses = `
    pdf-viewer-container
    ${className}
    ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : 'relative'}
    flex flex-col ${isFullscreen ? 'h-screen' : 'h-full'}
  `;

  return (
    <div className={containerClasses} tabIndex={0}>
      {/* Minimal PDF Controls - Clean Focus */}
      <div className="flex items-center justify-between px-3 py-2 bg-gray-800 text-white">
        {/* Left - Essential Zoom Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Zoom Out (-)"
            disabled={scale <= 0.5}
          >
            <ZoomOut size={14} />
          </button>
          
          <span className="text-xs text-gray-300 min-w-[45px] text-center">
            {Math.round(scale * 100)}%
          </span>
          
          <button
            onClick={handleZoomIn}
            className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Zoom In (+)"
            disabled={scale >= 3.0}
          >
            <ZoomIn size={14} />
          </button>
        </div>

        {/* Center - Essential Page Navigation */}
        {numPages > 0 && (
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrevPage}
              disabled={pageNumber <= 1}
              className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Previous Page (←)"
            >
              <ChevronLeft size={14} />
            </button>

            <div className="flex items-center space-x-1 text-xs">
              <span className="text-gray-300">{pageNumber}</span>
              <span className="text-gray-500">/</span>
              <span className="text-gray-300">{numPages}</span>
            </div>

            <button
              onClick={handleNextPage}
              disabled={pageNumber >= numPages}
              className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Next Page (→)"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        )}

        {/* Right - Fullscreen Only */}
        <div className="flex items-center">
          <button
            onClick={toggleFullscreen}
            className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title={isFullscreen ? "Exit Fullscreen (ESC)" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>

      {/* PDF Content Area - Clean Full Display */}
      <div 
        className="flex-1 bg-gray-900 pdf-content-area overflow-auto" 
        style={{ 
          height: isFullscreen ? 'calc(100vh - 44px)' : 'calc(100vh - 44px)',
          maxHeight: isFullscreen ? 'calc(100vh - 44px)' : '100%',
          minHeight: '400px',
          position: 'relative'
        }}
      >
        {error ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-400">
            <div className="text-lg font-medium mb-2">PDF nicht verfügbar</div>
            <div className="text-sm">{error}</div>
          </div>
        ) : (
          <div 
            className="pdf-document-container"
            style={{ 
              display: 'flex',
              justifyContent: scale <= 1.0 ? 'center' : 'flex-start',
              alignItems: 'flex-start',
              minWidth: 'fit-content',
              width: scale > 1.0 ? 'max-content' : '100%',
              minHeight: 'fit-content',
              padding: '2px'
            }}
          >
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
                  className="border border-gray-300 bg-white block"
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                  width={undefined}
                  height={undefined}
                />
              </Document>
          </div>
        )}
      </div>

      {/* Ultra Compact Status Bar */}
      <div className="px-2 py-0.5 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
        <div className="flex justify-between items-center">
          <div className="text-xs">
            {isLoading ? (
              'Loading...'
            ) : error ? (
              'Error'
            ) : (
              `Page ${pageNumber} of ${numPages} • ${Math.round(scale * 100)}%`
            )}
          </div>
          {!isLoading && !error && (
            <div className="text-gray-400 hidden sm:block text-xs">
              {isFullscreen ? (
                'ESC: Exit • ←→: Pages • ±: Zoom'
              ) : (
                'Ctrl+F: Fullscreen • ←→: Pages • ±: Zoom'
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
