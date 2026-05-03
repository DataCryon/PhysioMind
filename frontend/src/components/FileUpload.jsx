/**
 * FileUpload component — Drag-and-drop PDF upload zone.
 */

import { useState, useRef } from 'react';
import { HiOutlineCloudArrowUp, HiOutlineDocumentPlus } from 'react-icons/hi2';
import './FileUpload.css';

export default function FileUpload({ onUpload, uploading, uploadProgress }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find((f) => f.type === 'application/pdf');

    if (pdfFile) {
      onUpload(pdfFile);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
      // Reset input so same file can be re-uploaded
      e.target.value = '';
    }
  };

  const handleClick = () => {
    if (!uploading) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div
      className={`file-upload ${isDragOver ? 'drag-over' : ''} ${uploading ? 'uploading' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      id="file-upload-zone"
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleFileSelect}
        className="file-input-hidden"
        id="pdf-file-input"
      />

      {uploading ? (
        <div className="upload-progress">
          <div className="progress-spinner" />
          <p className="upload-status">Processing document...</p>
          <div className="progress-bar-container">
            <div
              className="progress-bar-fill"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          <span className="progress-percent">{uploadProgress}%</span>
        </div>
      ) : (
        <div className="upload-content">
          <div className="upload-icon-wrapper">
            {isDragOver ? (
              <HiOutlineDocumentPlus className="upload-icon active" />
            ) : (
              <HiOutlineCloudArrowUp className="upload-icon" />
            )}
          </div>
          <p className="upload-title">
            {isDragOver ? 'Drop your PDF here' : 'Upload PDF Document'}
          </p>
          <p className="upload-subtitle">
            Drag & drop or click to browse
          </p>
          <span className="upload-hint">PDF files only • Max 50MB</span>
        </div>
      )}
    </div>
  );
}
