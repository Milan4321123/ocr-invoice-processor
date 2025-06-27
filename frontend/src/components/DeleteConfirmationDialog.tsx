'use client'

import React, { useState } from 'react'
import { AlertTriangle, X } from 'lucide-react'

interface DeleteConfirmationDialogProps {
  isOpen: boolean
  fileName: string
  onConfirm: (alsoDeleteFromFolder?: boolean) => void
  onCancel: () => void
  uploadSource?: 'drag-drop' | 'folder-watcher' | 'manual' | 'unknown'
}

export default function DeleteConfirmationDialog({
  isOpen,
  fileName,
  onConfirm,
  onCancel,
  uploadSource = 'unknown'
}: DeleteConfirmationDialogProps) {
  const [confirmText, setConfirmText] = useState('')
  const [isSecondStep, setIsSecondStep] = useState(false)
  const [alsoDeleteFromFolder, setAlsoDeleteFromFolder] = useState(false)

  if (!isOpen) return null

  const getUploadSourceText = () => {
    switch (uploadSource) {
      case 'folder-watcher':
        return 'Diese Rechnung wurde automatisch über den Ordner-Watcher hochgeladen.'
      case 'drag-drop':
        return 'Diese Rechnung wurde per Drag & Drop hochgeladen.'
      case 'manual':
        return 'Diese Rechnung wurde manuell hochgeladen.'
      default:
        return 'Diese Rechnung wurde hochgeladen.'
    }
  }

  const getWarningText = () => {
    if (uploadSource === 'folder-watcher') {
      return 'Achtung: Wenn Sie diese Datei löschen, wird sie nicht automatisch erneut hochgeladen, auch wenn sie noch im überwachten Ordner vorhanden ist.'
    }
    return 'Diese Aktion kann nicht rückgängig gemacht werden.'
  }

  const handleFirstConfirm = () => {
    setIsSecondStep(true)
  }

  const handleFinalConfirm = () => {
    if (confirmText.toLowerCase() === 'löschen') {
      onConfirm()
      // Reset state
      setIsSecondStep(false)
      setConfirmText('')
    }
  }

  const handleCancel = () => {
    onCancel()
    // Reset state
    setIsSecondStep(false)
    setConfirmText('')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-6 w-6 text-red-600" />
            <h3 className="text-lg font-semibold text-gray-900">
              Rechnung löschen
            </h3>
          </div>
          <button
            onClick={handleCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {!isSecondStep ? (
          <>
            <div className="mb-4">
              <p className="text-gray-700 mb-2">
                Möchten Sie die folgende Rechnung wirklich löschen?
              </p>
              <div className="bg-gray-50 p-3 rounded-md mb-3">
                <p className="font-medium text-gray-900">{fileName}</p>
                <p className="text-sm text-gray-600 mt-1">{getUploadSourceText()}</p>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <p className="text-sm text-yellow-800">{getWarningText()}</p>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleCancel}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={handleFirstConfirm}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Ja, löschen
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="mb-4">
              <p className="text-gray-700 mb-3">
                Sind Sie sich absolut sicher? Diese Aktion kann nicht rückgängig gemacht werden.
              </p>
              <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
                <p className="text-sm text-red-800 font-medium mb-2">
                  Geben Sie "LÖSCHEN" ein, um zu bestätigen:
                </p>
                <input
                  type="text"
                  value={confirmText}
                  onChange={(e) => setConfirmText(e.target.value)}
                  placeholder="Geben Sie LÖSCHEN ein..."
                  className="w-full px-3 py-2 border border-red-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  autoFocus
                />
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleCancel}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={handleFinalConfirm}
                disabled={confirmText.toLowerCase() !== 'löschen'}
                className={`flex-1 px-4 py-2 rounded-md transition-colors ${
                  confirmText.toLowerCase() === 'löschen'
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Endgültig löschen
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
