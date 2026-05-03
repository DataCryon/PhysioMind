/**
 * SourceChip component — Displays a source attribution pill.
 */

import { HiOutlineDocumentText } from 'react-icons/hi2';
import './SourceChip.css';

export default function SourceChip({ fileName, pageNumber, relevanceScore }) {
  return (
    <span className="source-chip" title={`Relevance: ${(relevanceScore * 100).toFixed(0)}%`}>
      <HiOutlineDocumentText className="source-chip-icon" />
      <span className="source-chip-name">{fileName}</span>
      <span className="source-chip-page">Page {pageNumber}</span>
    </span>
  );
}
