importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

const firebaseConfig = {
  apiKey: "AIzaSyDPVRbcbayAK7L2lmFaaFWre1oEzoHjdZw",
  authDomain: "omni-4073a.firebaseapp.com",
  projectId: "omni-4073a",
  storageBucket: "omni-4073a.firebasestorage.app",
  messagingSenderId: "812026584834",
  appId: "1:812026584834:web:5a365c144e95abfad9ac1b",
  measurementId: "G-K4M5Y2VB88"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('Received background message: ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: 'https://cdn-icons-png.flaticon.com/512/564/564619.png'
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});