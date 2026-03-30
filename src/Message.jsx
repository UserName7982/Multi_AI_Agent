import { useRef, useState } from "react";
import { FiSend } from "react-icons/fi";

export function Message({ onSend }) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef(null);

  const handleInput = (e) => {
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  };

  const Sendmessage = async () => {
    if (!message.trim()) return;

    const userText = message;

    // send to parent (UI update)
    onSend(userText);

    // clear input
    setMessage("");
    textareaRef.current.style.height = "auto";
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto rounded-3xl border border-gray-700 bg-gray-800 p-3 shadow-sm">
      <textarea
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            Sendmessage();
          }
        }}
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onInput={handleInput}
        rows={1}
        placeholder="Message..."
        className="w-full min-h-10 max-h-40 resize-none overflow-y-auto bg-transparent text-white outline-none pr-12 text-xl"
      />

      <button
        onClick={Sendmessage}
        disabled={!message}
        className={`absolute right-4 bottom-4 p-2 rounded-full ${
          message ? "bg-gray-600 hover:bg-gray-400" : "bg-gray-600"
        }`}
      >
        {" "}
        <FiSend size={20} className="text-white" />
      </button>
    </div>
  );
}
