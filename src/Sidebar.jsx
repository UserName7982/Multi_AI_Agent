import { useState, useEffect } from "react";
import { FaPlus } from "react-icons/fa";
import galleryIcon from "./assets/image/plus.png";
export function SideBar({setCurrentThread}) {
  const [thread, setThread] = useState([]);
  const [activethread, setactivethread] = useState(null);
  const [title, settitile] = useState("");
  const [showoutput, setshowoutput] = useState(false);

  const fetchThreads = async () => {
    try {
      const response = await fetch("http://localhost:8000/app/get-threads", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();
      if (!Array.isArray(data) || data.length === 0) {
        setThread([]);
        return;
      }
      setThread(Array.isArray(data)?data.map((t) => ({ thread_id: t.thread_id, title: t.title })): []);
    } catch (error) {
      console.error(error);
    }
  }
  const create_thread = async () => {
    try {
      const response = await fetch("http://localhost:8000/app/new-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "user",
          title: title,
        }),
      });
      const data = await response.json();
      console.log(data);
      setThread((prev) => [data, ...prev]);
      setactivethread(data.thread_id);
      setCurrentThread(data.thread_id);
      settitile("");
      setshowoutput(false);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchThreads();
    console.log("fetching threads:", thread);
  }, []);
  return (
    <>
      <aside className="w-80 bg-gray-800 text-white p-4 flex flex-col shrink-0">
        <button
          onClick={() => setshowoutput(true)}
          className="border border-gray-700 p-2 mb-4 rounded-e-4xl rounded-b-4xl rounded-tl-4xl hover:bg-gray-700"
        >
         <img src={galleryIcon} alt="New Chat" className="w-4 h-4 inline-block mr-2" />
          New Chat
        </button>
        {showoutput && (
          <div className="mb-2">
            <input
              value={title}
              onChange={(e) => settitile(e.target.value)}
              placeholder="Enter title..."
              className="w-full px-3 py-2 rounded bg-gray-700 text-white outline-none"
            />

            <button
              onClick={create_thread}
              className="mt-1 w-full bg-blue-600 p-1 rounded"
            >
              Create
            </button>
          </div>
        )}
        <div className="flex flex-col gap-1">
          {thread.map((t) => (
            <div
              key={t.thread_id}
              onClick={() => {
                setactivethread(t.thread_id);
                setCurrentThread(t.thread_id);
              }}
              className={`p-2 rounded cursor-pointer ${
                activethread === t.thread_id
                  ? "bg-gray-700 text-yellow-100 font-black text-center"
                  : "hover:bg-gray-500 text-yellow-100 font-light text-center"
              }`}
            >
              {t.title}
            </div>
          ))}
        </div>
      </aside>
    </>
  );
}
