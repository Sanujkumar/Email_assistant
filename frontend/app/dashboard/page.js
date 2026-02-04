'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { chatAPI, emailAPI } from '@/lib/api';
import ChatMessage from '@/components/ChatMessage';
import EmailCard from '@/components/EmailCard';

export default function Dashboard() {
  const router = useRouter();
  const { user, isAuthenticated, loading, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [emails, setEmails] = useState([]);
  const [pendingAction, setPendingAction] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(() => {
    if (user && messages.length === 0) {
      // Welcome message
      addBotMessage(
        `Hello ${user.name}! 👋 Welcome to your Gmail AI Assistant.\n\nI can help you with:\n• Reading and summarizing your emails\n• Generating professional replies\n• Deleting unwanted emails\n• Searching your inbox\n• Creating daily digests\n\nWhat would you like to do?`
      );
    }
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addBotMessage = (text, action = null, data = null) => {
    const message = {
      id: Date.now() + Math.random(),
      text,
      sender: 'bot',
      timestamp: new Date(),
      action,
      data
    };
    setMessages(prev => [...prev, message]);
  };

  const addUserMessage = (text) => {
    const message = {
      id: Date.now() + Math.random(),
      text,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    const userMsg = inputMessage.trim();
    setInputMessage('');
    addUserMessage(userMsg);
    setIsSending(true);

    try {
      const response = await chatAPI.sendMessage(userMsg);
      
      addBotMessage(response.response, response.action, response.data);
      
      // Handle specific actions
      if (response.action === 'list_emails' && response.data?.emails) {
        setEmails(response.data.emails);
      }
    } catch (error) {
      console.error('Send message error:', error);
      addBotMessage('Sorry, I encountered an error processing your request. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const handleGenerateReply = async (emailId) => {
    setIsSending(true);
    try {
      const response = await emailAPI.generateReply(emailId);
      addBotMessage(`Here's a suggested reply:\n\n"${response.reply}"\n\nWould you like to send this reply? (Type 'send reply' to confirm)`);
      setPendingAction({ type: 'send_reply', emailId, reply: response.reply });
    } catch (error) {
      console.error('Generate reply error:', error);
      addBotMessage('Failed to generate reply. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const handleSendReply = async (emailId, replyContent) => {
    setIsSending(true);
    try {
      await emailAPI.sendReply(emailId, replyContent);
      addBotMessage('Reply sent successfully! ✅');
      setPendingAction(null);
    } catch (error) {
      console.error('Send reply error:', error);
      addBotMessage('Failed to send reply. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const handleDeleteEmail = async (emailId) => {
    setIsSending(true);
    try {
      await emailAPI.deleteEmail(emailId);
      addBotMessage('Email deleted successfully! 🗑️');
      // Remove from local state
      setEmails(prev => prev.filter(e => e.id !== emailId));
    } catch (error) {
      console.error('Delete email error:', error);
      addBotMessage('Failed to delete email. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Gmail AI Assistant</h1>
              <p className="text-sm text-gray-500">Powered by AI</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-800">{user.name}</p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>
            {user.picture && (
              <img src={user.picture} alt={user.name} className="w-10 h-10 rounded-full" />
            )}
            <button
              onClick={handleLogout}
              className="ml-2 px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <div className="max-w-7xl mx-auto h-full flex flex-col lg:flex-row p-6 gap-6">
          {/* Chat Area */}
          <div className="flex-1 bg-white rounded-xl shadow-lg flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-800">Chat Assistant</h2>
            </div>
            
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map(message => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            {/* Input */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message... (e.g., 'show my emails', 'delete email 2')"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isSending}
                />
                <button
                  type="submit"
                  disabled={isSending || !inputMessage.trim()}
                  className="px-6 py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSending ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    'Send'
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Emails Sidebar */}
          {emails.length > 0 && (
            <div className="lg:w-96 bg-white rounded-xl shadow-lg flex flex-col max-h-[calc(100vh-200px)]">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-800">Recent Emails</h2>
              </div>
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {emails.map((email, index) => (
                  <EmailCard
                    key={email.id}
                    email={email}
                    number={email.number || index + 1}
                    onGenerateReply={handleGenerateReply}
                    onDelete={handleDeleteEmail}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
