import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')  // ⚠️ mount app đã tạo, không gọi createApp lần nữa!


// Firebase
import { initializeApp } from "firebase/app";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";

// Cấu hình Firebase
const firebaseConfig = {
  apiKey: "AIzaSyD2DkkELUpKiRov5I-wr6UdePB_44G1G9g",
  authDomain: "studyflow-651a1.firebaseapp.com",
  projectId: "studyflow-651a1",
  storageBucket: "studyflow-651a1.firebasestorage.app",
  messagingSenderId: "99772491196",
  appId: "1:99772491196:web:42940934e85b34db78b7b9",
  measurementId: "G-V4555EY1DK"
};


// Khởi tạo Firebase
const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);

// Khởi tạo provider cho Google & Facebook
const googleProvider = new GoogleAuthProvider();

// Xuất các hàm cần dùng
export { auth, googleProvider, signInWithPopup };