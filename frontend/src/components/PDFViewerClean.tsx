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
  X
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
  onShowBottomInfo?: (show: boolean) => void;
}

export default function PDFViewer({ 
  pdfUrl, 
  onLoadSuccess, 
  onLoadError,
  className = "",
  onShowBottomInfo
}: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showToolbar, setShowToolbar] = useState<boolean>(false);

  const onDocumentLoadSuccess = useCallback(({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setPageNumber(1);
    setIsLoading(false);
    setError(null);
    onLoadSuccess?.(numPages);
  }, [onLoadSuccess]);

  const onDocumentLoadError = useCallback((error: any) => {
    console.error('PDF loading error:', error);
    setError(`Failed to load PDF: ${error.message || error.toString()}`);
    setIsLoading(false);
    onLoadError?.(error);
  }, [onLoadError]);

  // Handle scroll to show/hide toolbar
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.target as HTMLDivElement;
    const { scrollTop, scrollHeight, clientHeight } = target;
    const isNearBottom = scrollTop + clientHeight >= scrollHeight - 50; // 50px threshold
    setShowToolbar(isNearBottom);
    onShowBottomInfo?.(isNearBottom); // Trigger bottom info panel in parent
  };

  // Navigation functions
  const handlePrevPage = () => {
    setPageNumber(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setPageNumber(prev => Math.min(prev + 1, numPages));
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.25, 3.0));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handleFullscreen = () => {
    setIsFullscreen(prev => !prev);
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
            setIsFullscreen(true);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen, pageNumber, numPages, scale]);

  const containerClasses = `
    pdf-viewer-container
    ${className}
    ${isFullscreen ? 'fixed inset-0 z-50 bg-gray-900' : 'relative'}
    flex flex-col ${isFullscreen ? 'h-screen' : 'h-full'}
  `;

  return (
    <div className={containerClasses} tabIndex={0}>
      {/* Clean PDF Content Area - Full Display */}
      <div 
        className="flex-1 bg-gray-900 pdf-content-area overflow-auto relative" 
        style={{ 
          height: isFullscreen ? '100vh' : '100%',
          minHeight: '400px'
        }}
        onScroll={handleScroll}
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
              padding: '20px'
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
                  className="pdf-page"
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                />
              </Document>
          </div>
        )}
        
        {/* Floating PDF Toolbar - Only visible when scrolled to bottom */}
        {showToolbar && (
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white rounded-lg shadow-lg px-4 py-2 z-20">
            <div className="flex items-center space-x-4">
              {/* Zoom Controls */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleZoomOut}
                  className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
                  title="Zoom Out (-)"
                  disabled={scale <= 0.5}
                >
                  <ZoomOut size={16} />
                </button>
                
                <span className="text-sm text-gray-300 min-w-[50px] text-center">
                  {Math.round(scale * 100)}%
                </span>
                
                <button
                  onClick={handleZoomIn}
                  className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
                  title="Zoom In (+)"
                  disabled={scale >= 3.0}
                >
                  <ZoomIn size={16} />
                </button>
              </div>

              {/* Page Navigation */}
              {numPages > 0 && (
                <div className="flex items-center space-x-2 border-l border-gray-600 pl-4">
                  <button
                    onClick={handlePrevPage}
                    disabled={pageNumber <= 1}
                    className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Vorherige Seite (←)"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  
                  <span className="text-sm text-gray-300 min-w-[60px] text-center">
                    {pageNumber} / {numPages}
                  </span>
                  
                  <button
                    onClick={handleNextPage}
                    disabled={pageNumber >= numPages}
                    className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Nächste Seite (→)"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              )}

              {/* Additional Controls */}
              <div className="flex items-center space-x-2 border-l border-gray-600 pl-4">
                <button
                  onClick={handleRotate}
                  className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
                  title="Drehen"
                >
                  <RotateCw size={16} />
                </button>
                
                <button
                  onClick={handleFullscreen}
                  className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
                  title={isFullscreen ? 'Vollbild verlassen (Esc)' : 'Vollbild (F)'}
                >
                  {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                </button>
                
                <button
                  onClick={handleDownload}
                  className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
                  title="PDF herunterladen"
                >
                  <Download size={16} />
                </button>

                {isFullscreen && (
                  <button
                    onClick={() => setIsFullscreen(false)}
                    className="p-1 text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
                    title="Schließen (Esc)"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
