import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";


const firebaseConfig = {
  apiKey: "AIzaSyDPVRbcbayAK7L2lmFaaFWre1oEzoHjdZw",
  authDomain: "omni-4073a.firebaseapp.com",
  projectId: "omni-4073a",
  storageBucket: "omni-4073a.firebasestorage.app",
  messagingSenderId: "812026584834",
  appId: "1:812026584834:web:5a365c144e95abfad9ac1b",
  measurementId: "G-K4M5Y2VB88"
};

const app = initializeApp(firebaseConfig);

let messaging: any;
try {
  messaging = getMessaging(app);
} catch (error) {
  console.warn("Firebase Messaging not fully configured yet.");
}

export { messaging, getToken, onMessage };