/**
 * Layout component — App shell with sidebar navigation.
 */

import { NavLink, useLocation } from 'react-router-dom';
import { HiOutlineDocumentText, HiOutlineChatBubbleLeftRight, HiOutlineSparkles } from 'react-icons/hi2';
import './Layout.css';

export default function Layout({ children }) {
  const location = useLocation();

  return (
    <div className="layout">
      {/* Sidebar (Desktop) */}
      <aside className="sidebar glass desktop-only">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <HiOutlineSparkles />
          </div>
          <div className="brand-text">
            <h1 className="brand-name">PhysioMind</h1>
            <span className="brand-tagline">AI Document Assistant</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink
            to="/"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            end
          >
            <HiOutlineDocumentText className="nav-icon" />
            <span>Documents</span>
          </NavLink>

          <NavLink
            to="/chat"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <HiOutlineChatBubbleLeftRight className="nav-icon" />
            <span>Chat</span>
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <p className="footer-text">Powered by Groq + LangChain</p>
        </div>
      </aside>

      {/* Mobile Header */}
      <header className="mobile-header mobile-only glass">
        <div className="brand-icon-sm">
          <HiOutlineSparkles />
        </div>
        <h1 className="brand-name-sm">PhysioMind</h1>
      </header>

      {/* Main content */}
      <main className="main-content">
        {children}
      </main>

      {/* Bottom Navigation (Mobile) */}
      <nav className="bottom-nav mobile-only glass">
        <NavLink
          to="/"
          className={({ isActive }) => `bottom-nav-link ${isActive ? 'active' : ''}`}
          end
        >
          <HiOutlineDocumentText className="nav-icon" />
          <span>Docs</span>
        </NavLink>

        <NavLink
          to="/chat"
          className={({ isActive }) => `bottom-nav-link ${isActive ? 'active' : ''}`}
        >
          <HiOutlineChatBubbleLeftRight className="nav-icon" />
          <span>Chat</span>
        </NavLink>
      </nav>
    </div>
  );
}
