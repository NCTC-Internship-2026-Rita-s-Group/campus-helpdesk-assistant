import React from "react";

import ReactDOM from "react-dom/client";

import App from "./App.tsx";

import { AuthProvider } from "./context/AuthContext.tsx"; // 🔑 Import our security session wrapper

import "./index.css"; // Your mind-blowing tailwind/css configurations

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {/* 🛡️ Injecting the enterprise authentication provider context grid */}

    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
);
