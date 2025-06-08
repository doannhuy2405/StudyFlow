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
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Khởi tạo provider cho Google 
const googleProvider = new GoogleAuthProvider();

// Xuất các hàm cần dùng
export { auth, googleProvider, signInWithPopup };
