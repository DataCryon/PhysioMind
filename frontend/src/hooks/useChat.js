/**
 * useChat hook — manages chat state and Q&A operations.
 */

import { useState, useCallback, useEffect } from 'react';
import { askQuestion, getSessions, createSession, getSessionMessages, deleteSession as apiDeleteSession } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load all sessions on mount
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data);
    } catch (err) {
      console.error("Failed to fetch sessions", err);
    }
  };

  const selectSession = async (sessionId) => {
    setCurrentSessionId(sessionId);
    setLoading(true);
    try {
      const history = await getSessionMessages(sessionId);
      const formattedMessages = history.map(m => ({
        id: m.id,
        role: m.role,
        content: m.content,
        timestamp: m.created_at
      }));
      setMessages(formattedMessages);
    } catch (err) {
      setError("Failed to load conversation history");
    } finally {
      setLoading(false);
    }
  };

  const startNewSession = async () => {
    try {
      const newSession = await createSession("New Conversation");
      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
      setMessages([]);
    } catch (err) {
      setError("Failed to create new chat");
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      await apiDeleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null);
        setMessages([]);
      }
    } catch (err) {
      setError("Failed to delete session");
    }
  };

  /** Send a question and receive an answer with sources. */
  const ask = useCallback(async (question, fileId = null, systemPrompt = null) => {
    if (!question.trim() || loading) return;

    let sessionId = currentSessionId;
    
    // Auto-create session if none exists
    if (!sessionId) {
      try {
        const newSession = await createSession(question.slice(0, 30));
        sessionId = newSession.id;
        setCurrentSessionId(sessionId);
        setSessions(prev => [newSession, ...prev]);
      } catch (err) {
        setError("Failed to initialize session");
        return;
      }
    }

    const historyForApi = messages.slice(-4);
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const result = await askQuestion(question, historyForApi, fileId, systemPrompt, sessionId);

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.answer,
        sources: result.sources || [],
        chunksUsed: result.chunks_used || 0,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      
      // Refresh sessions to update title if changed
      fetchSessions();
      
      return result;
    } catch (err) {
      setError(err.message);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.message}`,
        isError: true,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }, [messages, loading, currentSessionId]);

  /** Clear all chat messages in current view. */
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    sessions,
    currentSessionId,
    loading,
    error,
    ask,
    clearChat,
    selectSession,
    startNewSession,
    deleteSession
  };
}
