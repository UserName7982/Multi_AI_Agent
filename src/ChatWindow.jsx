import { Message } from "./Message";
import { useEffect, useState, useRef, use } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { TypingIndicator } from "./TypingIndicator";
export function ChatWindow({ currentThread }) {
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null);
  const scrollRef = useRef(false);
  const userScroll = useRef(false);
  let [loading, setLoading] = useState(false);
  let flush = useRef(null);

  const fetchMessages = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/app/get-messages/${currentThread}`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        },
      );

      if (response.ok) {
        const data = await response.json();
        if (data.length === 0) {
          setMessages([]);
          return;
        }
        setMessages(Array.isArray(data)?
          data.map((msg) => ({
            type: msg.role === "user" ? "user" : "ai",
            text: msg.content,
          })): [],
        );
      } else {
        console.error("Failed to fetch messages");
      }
    } catch (e) {
      console.error(e);
    }
  };
  const handleScroll = () => {
    const el = scrollRef.current;
    if (!el) return;

    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 20;

    if (atBottom) {
      userScroll.current = false;
    } else {
      userScroll.current = true;
    }
  };
  useEffect(() => {
    if (currentThread === null) return;
    setMessages([]);
    fetchMessages();
  }, [currentThread]);

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
          Thread: currentThread,
        }),
      });
      if (!res.body) throw new Error("No response body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let firstchunk = true;
      let buffer = "";
      flush.current = setInterval(() => {
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
      clearInterval(flush.current);
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
      clearInterval(flush.current);
      setLoading(false);
    }
  };

  return (
    <>
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
    </>
  );
}
