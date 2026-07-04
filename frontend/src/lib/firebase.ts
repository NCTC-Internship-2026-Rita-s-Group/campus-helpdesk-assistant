import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// 📋 Safely map our Vite environment configuration matrix
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// 🛡️ Fail-safe structural assertion during development cycles
if (!firebaseConfig.apiKey) {
  console.error(
    "❌ Configuration Alert: Firebase API Key is missing! " +
      "Verify that your .env.local file is configured perfectly at the root of your project.",
  );
}

// 🚀 Boot up the Firebase application context
const app = initializeApp(firebaseConfig);

// 🔑 Instantiate the global authentication state manager
export const auth = getAuth(app);
export default app;
