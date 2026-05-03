/**
 * Dashboard page — PDF upload and document management.
 */

import toast from 'react-hot-toast';
import { HiOutlineDocumentText, HiOutlineRectangleStack } from 'react-icons/hi2';
import { useDocuments } from '../hooks/useDocuments';
import FileUpload from '../components/FileUpload';
import DocumentList from '../components/DocumentList';
import './Dashboard.css';

export default function Dashboard() {
  const {
    documents,
    loading,
    uploading,
    uploadProgress,
    upload,
    remove,
  } = useDocuments();

  const handleUpload = async (file) => {
    try {
      const result = await upload(file);
      toast.success(
        `"${result.file_name}" uploaded successfully — ${result.page_count} pages, ${result.chunk_count} chunks indexed`,
        { duration: 4000 }
      );
    } catch (err) {
      toast.error(`Upload failed: ${err.message}`);
    }
  };

  const handleDelete = async (fileId) => {
    try {
      await remove(fileId);
      toast.success('Document deleted successfully');
    } catch (err) {
      toast.error(`Delete failed: ${err.message}`);
    }
  };

  // Stats
  const totalDocs = documents.length;
  const totalPages = documents.reduce((sum, doc) => sum + (doc.page_count || 0), 0);
  const totalChunks = documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0);

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="page-header animate-fade-in">
        <div>
          <h1 className="page-title">Document <span className="gradient-text">Dashboard</span></h1>
          <p className="page-subtitle">Upload and manage your PDF documents for AI-powered Q&A</p>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-row animate-fade-in" style={{ animationDelay: '0.1s' }}>
        <div className="stat-card glass">
          <div className="stat-icon">
            <HiOutlineDocumentText />
          </div>
          <div className="stat-info">
            <span className="stat-value">{totalDocs}</span>
            <span className="stat-label">Documents</span>
          </div>
        </div>
        <div className="stat-card glass">
          <div className="stat-icon">
            <HiOutlineRectangleStack />
          </div>
          <div className="stat-info">
            <span className="stat-value">{totalPages}</span>
            <span className="stat-label">Total Pages</span>
          </div>
        </div>
        <div className="stat-card glass">
          <div className="stat-icon chunks">
            <HiOutlineRectangleStack />
          </div>
          <div className="stat-info">
            <span className="stat-value">{totalChunks}</span>
            <span className="stat-label">Indexed Chunks</span>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      <section className="section animate-fade-in" style={{ animationDelay: '0.15s' }}>
        <h2 className="section-title">Upload Document</h2>
        <FileUpload
          onUpload={handleUpload}
          uploading={uploading}
          uploadProgress={uploadProgress}
        />
      </section>

      {/* Document List */}
      <section className="section animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <h2 className="section-title">
          Your Documents
          {totalDocs > 0 && <span className="section-count">{totalDocs}</span>}
        </h2>
        <DocumentList
          documents={documents}
          loading={loading}
          onDelete={handleDelete}
        />
      </section>
    </div>
  );
}
