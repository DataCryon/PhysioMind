/**
 * useDocuments hook — manages document state and operations.
 */

import { useState, useEffect, useCallback } from 'react';
import { getDocuments, uploadDocument, deleteDocument } from '../services/api';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  /** Fetch all documents from the API. */
  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch documents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /** Upload a new PDF document. */
  const upload = useCallback(async (file) => {
    try {
      setUploading(true);
      setUploadProgress(0);
      setError(null);

      const result = await uploadDocument(file, (progress) => {
        setUploadProgress(progress);
      });

      // Refresh document list after successful upload
      await fetchDocuments();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [fetchDocuments]);

  /** Remove a document by ID. */
  const remove = useCallback(async (fileId) => {
    try {
      setError(null);
      await deleteDocument(fileId);
      // Optimistic removal from local state
      setDocuments((prev) => prev.filter((doc) => doc.id !== fileId));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  // Load documents on mount
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  return {
    documents,
    loading,
    uploading,
    uploadProgress,
    error,
    fetchDocuments,
    upload,
    remove,
  };
}
