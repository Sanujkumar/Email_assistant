import { useState } from 'react';

export default function EmailCard({ email, number, onGenerateReply, onDelete }) {
  const [showActions, setShowActions] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this email?')) {
      setIsDeleting(true);
      await onDelete(email.id);
    }
  };

  return (
    <div
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <span className="inline-flex items-center justify-center w-6 h-6 text-xs font-bold text-white bg-blue-500 rounded-full">
              {number}
            </span>
            <h3 className="font-semibold text-gray-800 text-sm truncate">
              {email.sender_name}
            </h3>
          </div>
          <p className="text-xs text-gray-500 mb-1">{email.sender_email}</p>
          <p className="text-sm font-medium text-gray-700 mb-2 line-clamp-1">
            {email.subject}
          </p>
        </div>
      </div>

      <p className="text-xs text-gray-600 mb-3 line-clamp-3">
        {email.summary || email.snippet}
      </p>

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">
          {new Date(email.date).toLocaleDateString()}
        </span>

        {showActions && (
          <div className="flex space-x-2">
            <button
              onClick={() => onGenerateReply(email.id)}
              className="px-3 py-1 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded transition-colors"
            >
              Reply
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
