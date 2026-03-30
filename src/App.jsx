import "./App.css";
import { Message } from "./Message";
import { useEffect, useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { TypingIndicator } from "./TypingIndicator";
function App() {
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null);
  const scrollRef = useRef(false);
  const userScroll = useRef(false);
  let [loading, setLoading] = useState(false);
  let flush = null;

  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;

    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 20;

    userScroll.current = !atBottom; // true = user scrolled up
  };

  useEffect(() => {
    if (!userScroll.current) {
      setTimeout(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 0);
    }
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { type: "user", text }]);
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/app/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: text,
          Thread: 4, 
        }),
      });
      if (!res.body) throw new Error("No response body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let firstchunk = true;
      let buffer = "";
      flush = setInterval(() => {
        if (buffer.length === 0) return;
        const toFlush = buffer;
        buffer = "";
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.type === "ai") {
            return [
              ...prev.slice(0, -1),
              { ...last, text: last.text + toFlush },
            ];
          }
          return prev;
        });
      }, 50);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        if (firstchunk) {
          setLoading(false);
          setMessages((prev) => [...prev, { type: "ai", text: "" }]);
          firstchunk = false;
        }

        buffer += chunk;
      }

      // flush remaining buffer
      clearInterval(flush);
      if (buffer.length > 0) {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.type === "ai") {
            return [
              ...prev.slice(0, -1),
              { ...last, text: last.text + buffer },
            ];
          }
          return prev;
        });
      }
    } catch (e) {
      console.error(e);
    } finally {
      clearInterval(flush);
      setLoading(false);
    }
  };
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-80 bg-gray-800 text-white p-4 flex flex-col shrink-0">
        <button className="border border-gray-700 p-2 mb-4">+ New Chat</button>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-16 border-b border-gray-700 flex items-center px-6 bg-gray-900 shrink-0">
          <h1 className="text-white text-2xl">Personal AI Assistant</h1>
        </div>

        {/* Messages + Input */}
        <div className="flex flex-col flex-1 bg-gray-900 overflow-hidden">
          {/* Messages */}
          <div
            id="Message_id"
            ref={scrollRef}
            onScroll={handleScroll}
            className="flex-1 overflow-y-auto px-6 py-4"
          >
            <div className="max-w-5xl mx-auto space-y-4">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center">
                  <div className="text-gray-400 text-4xl text-center">
                    Start a conversation with your Personal AI 🚀
                  </div>
                </div>
              ) : (
                messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${
                      msg.type === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`px-4 py-2 rounded-xl max-w-[70%] ${
                        msg.type === "user"
                          ? "bg-slate-700 text-xl text-gray-300"
                          : "bg-slate-900 text-xl text-gray-200"
                      }`}
                    >
                      {msg.type === "user" ? (
                        msg.text
                      ) : (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]} 
                          components={{
                            code({
                              node,
                              inline,
                              className,
                              children,
                              ...props
                            }) {
                              const match = /language-(\w+)/.exec(
                                className || "",
                              );
                              return !inline && match ? (
                                <SyntaxHighlighter
                                  style={oneDark}
                                  language={match[1]}
                                  PreTag="div"
                                  {...props}
                                >
                                  {String(children).replace(/\n$/, "")}
                                </SyntaxHighlighter>
                              ) : (
                                <code
                                  className="bg-gray-700 px-1 rounded"
                                  {...props}
                                >
                                  {children}
                                </code>
                              );
                            },
                          }}
                        >
                          {msg.text}
                        </ReactMarkdown>
                      )}
                    </div>
                  </div>
                ))
              )}
              {loading && <TypingIndicator />}
              <div ref={bottomRef}></div>
            </div>
          </div>

          {/* Input */}
          <div className="p-4 shrink-0">
            <div className="max-w mx-auto">
              <Message onSend={sendMessage} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
