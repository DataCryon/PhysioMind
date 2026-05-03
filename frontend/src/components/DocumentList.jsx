/**
 * DocumentList component — Grid of uploaded PDF documents.
 */

import { useState } from 'react';
import { HiOutlineDocumentText, HiOutlineTrash, HiOutlineClock, HiOutlineRectangleStack } from 'react-icons/hi2';
import { formatFileSize, formatDate } from '../utils/formatters';
import './DocumentList.css';

export default function DocumentList({ documents, loading, onDelete }) {
  const [deletingId, setDeletingId] = useState(null);
  const [confirmId, setConfirmId] = useState(null);

  const handleDeleteClick = (docId) => {
    if (confirmId === docId) {
      // Second click = confirm delete
      handleConfirmDelete(docId);
    } else {
      // First click = show confirm state
      setConfirmId(docId);
      // Auto-reset after 3 seconds
      setTimeout(() => setConfirmId(null), 3000);
    }
  };

  const handleConfirmDelete = async (docId) => {
    try {
      setDeletingId(docId);
      setConfirmId(null);
      await onDelete(docId);
    } catch (err) {
      console.error('Delete failed:', err);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="document-grid">
        {[1, 2, 3].map((i) => (
          <div key={i} className="doc-card skeleton-card">
            <div className="skeleton" style={{ width: '40px', height: '40px', borderRadius: '10px' }} />
            <div className="skeleton" style={{ width: '70%', height: '16px' }} />
            <div className="skeleton" style={{ width: '50%', height: '12px' }} />
            <div className="skeleton" style={{ width: '40%', height: '12px' }} />
          </div>
        ))}
      </div>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="empty-state animate-fade-in">
        <div className="empty-icon-wrapper">
          <HiOutlineDocumentText className="empty-icon" />
        </div>
        <h3 className="empty-title">No documents yet</h3>
        <p className="empty-text">Upload your first PDF to get started with AI-powered Q&A</p>
      </div>
    );
  }

  return (
    <div className="document-grid">
      {documents.map((doc, idx) => (
        <div
          key={doc.id}
          className={`doc-card glass animate-fade-in ${deletingId === doc.id ? 'deleting' : ''}`}
          style={{ animationDelay: `${idx * 0.05}s` }}
        >
          <div className="doc-card-header">
            <div className="doc-icon">
              <HiOutlineDocumentText />
            </div>
            <button
              className={`btn btn-danger btn-sm ${confirmId === doc.id ? 'confirm' : ''}`}
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteClick(doc.id);
              }}
              disabled={deletingId === doc.id}
              title={confirmId === doc.id ? 'Click again to confirm' : 'Delete document'}
              id={`delete-doc-${doc.id}`}
            >
              <HiOutlineTrash />
              <span>{confirmId === doc.id ? 'Confirm?' : ''}</span>
            </button>
          </div>

          <h4 className="doc-name" title={doc.file_name}>{doc.file_name}</h4>

          <div className="doc-meta">
            <span className="meta-item">
              <HiOutlineRectangleStack />
              {doc.page_count} pages • {doc.chunk_count} chunks
            </span>
            <span className="meta-item">
              {formatFileSize(doc.file_size)}
            </span>
            <span className="meta-item">
              <HiOutlineClock />
              {formatDate(doc.created_at)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
