export default function ChatMessage({ message }) {
  const { text, sender, timestamp } = message;
  
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isBot = sender === 'bot';

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'}`}>
      <div className={`max-w-[75%] ${isBot ? '' : 'flex flex-col items-end'}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isBot
              ? 'bg-gray-100 text-gray-800 rounded-tl-none'
              : 'bg-blue-500 text-white rounded-tr-none'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap break-words">{text}</p>
        </div>
        <span className="text-xs text-gray-400 mt-1 px-2">
          {formatTime(timestamp)}
        </span>
      </div>
    </div>
  );
}
