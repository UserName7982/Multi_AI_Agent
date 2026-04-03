import "./App.css";
import { ChatWindow } from "./ChatWindow";
import { SideBar } from "./Sidebar";
import { useState } from "react";
function App() {
  const [currentThread, setCurrentThread] = useState(null);
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <SideBar {...{ setCurrentThread }} />
      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-16 border-b border-gray-700 flex items-center px-6 bg-gray-900 shrink-0">
          <h1 className="text-white text-2xl">Personal AI Assistant</h1>
        </div>
        {/* Message Windows+ Input */}
        {currentThread === null ? (
          <div className="flex-1 flex justify-center p-6 text-4xl text-gray-400 text-center">
              <p>
              <br/>
               Start a **New Chat** to begin
              
              something fresh, or jump back into one of your previous
              <br/>
              conversations anytime. Let’s build, explore, and get things done
              🚀
            </p>
          </div>
        ) : (
          <ChatWindow {...{ currentThread }} />
        )}
      </div>
    </div>
  );
}

export default App;
