// TypingIndicator.jsx
export function TypingIndicator() {
    return (
        <div className="flex justify-start">
            <div className="bg-slate-800 px-4 py-3 rounded-xl flex gap-1 items-center">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
            </div>
            <span>Thinking...</span>
        </div>
    );
}