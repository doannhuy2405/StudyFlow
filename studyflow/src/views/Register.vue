<template>
  <div class="register-page">
    
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
      <h1 style="font-size: 3.5em;">StudyFlow</h1>

      <!-- Khung đăng ký -->
         <div class="auth-form">
          <h2 id="registerTitle">Đăng ký</h2>
          <form @submit.prevent="handleSignUp">
            <div class="form-group">
              <label for="fullname">Họ và tên:</label>
              <input type="text" v-model="fullname" id="fullname" :placeholder="'Nhập họ và tên.....'" />
            </div>
            <div class="form-group">
              <label for="email">Email:</label>
              <input type="email" v-model="email" id="email" :placeholder="'Nhập email.....'" />
            </div>
            <div class="form-group">
              <label for="username">Tên đăng nhập:</label>
              <input type="text" v-model="username" id="username" :placeholder="'Nhập tên đăng nhập.....'" />
            </div>
            <div class="form-group">
              <label for="password">Mật khẩu:</label>
              <input type="password" v-model="password" id="password" :placeholder="'Nhập mật khẩu.....'" />
            </div>
            <div class="form-group">
              <label for="confirmPassword">Xác nhận mật khẩu:</label>
              <input type="password" v-model="confirmPassword" id="confirmPassword" :placeholder="'Nhập lại mật khẩu.....'" />
            </div>
            <button class="btn-login" id="registerButton">Đăng ký</button>

            <p>Hoặc đăng nhập với:</p>

            <div class="social-login">
              <button type="button" class="btn-login" @click="loginWithGoogle"><i class='bx bxl-google'></i>&nbsp;&nbsp;Đăng nhập với Google</button>
              <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
            </div>
          </form>
          
          <p class="signin-link">
              Bạn đã có tài khoản?
              <button class="btn-signin" @click="goToLogin">Đăng nhập</button>
            </p>
        </div>
        <!-- Kết thúc khung đăng ký -->

    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { useRouter } from 'vue-router';
import { ref, reactive } from 'vue';
import axios from "axios";
import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";

const router = useRouter();

const goToLogin = () => {
  router.push('/login');
}

// Đăng nhập Google với Firebase
const auth = getAuth();
const provider = new GoogleAuthProvider();

const loginWithGoogle = async () => {
  try {
    // 1. Đăng nhập bằng popup Google
    const result = await signInWithPopup(auth, provider)
    const user = result.user
    
    // 2. Lấy ID token
    const idToken = await user.getIdToken()
    console.log("Google ID Token:", idToken) // Debug token

    // 3. Gửi token lên backend
    const response = await axios.post("/api/auth/google-login", {
      token: idToken  
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 4. Xử lý kết quả
    if (response.data.success) {
      console.log("Đăng nhập thành công:", response.data)
      localStorage.setItem('token', response.data.token)
      router.push('/home') // Chuyển hướng sau khi đăng nhập
    } else {
      errors.google = response.data.message || "Đăng nhập thất bại"
    }
    
  } catch (error) {
    console.error("Lỗi đăng nhập Google:", error)
    
    // Phân loại lỗi chi tiết
    if (error.response) {
      // Lỗi từ phía server
      errors.google = error.response.data.detail || "Lỗi server"
    } else if (error.code === 'auth/popup-closed-by-user') {
      errors.google = "Bạn đã đóng cửa sổ đăng nhập"
    } else {
      errors.google = "Lỗi hệ thống, vui lòng thử lại"
    }
  }
}

// Khai báo biến
  const fullname = ref("");
  const email = ref("");
  const username = ref("");
  const password = ref("");
  const confirmPassword = ref("");

  //Khai báo errors 
  const errors = reactive({
    fullname: "",
    email: "",
    username: "",
    password: "",
    confirmPassword: ""
  });

  const handleSignUp = async () => {
  
  // Kiểm tra đầu vào trước khi gửi request
  errors.fullname = fullname.value ? "" : "Họ và tên không được để trống.";
  errors.email = email.value ? "" : "Email không được để trống.";
  errors.username = username.value ? "" : "Tên đăng nhập không được để trống.";
  errors.password = password.value ? "" : "Mật khẩu không được để trống.";
  errors.confirmPassword = confirmPassword.value ? "" : "Vui lòng xác nhận mật khẩu.";

  // Kiểm tra email hợp lệ
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    errors.email = "Email không hợp lệ.";
  }

  // 🔹 Kiểm tra mật khẩu tối thiểu 6 ký tự
  if (password.value.length < 6) {
    errors.password = "Mật khẩu phải có ít nhất 6 ký tự.";
  }

  // 🔹 Kiểm tra mật khẩu nhập lại có khớp không
  if (password.value !== confirmPassword.value) {
    errors.confirmPassword = "Mật khẩu xác nhận không khớp.";
  }

  // 🔹 Nếu có lỗi, dừng lại luôn
  if (
    errors.fullname || 
    errors.email || 
    errors.username || 
    errors.password || 
    errors.confirmPassword
  ) {
    alert("⚠️ Vui lòng kiểm tra lại thông tin đăng ký!");
    return;
  }

  try {
    console.log("Bắt đầu gửi request đăng ký...");

    const response = await axios.post("/api/auth/register", {
      fullname: fullname.value,
      email: email.value,
      username: username.value,
      password: password.value
    });
    console.log(response);

    const { token, user } = response.data;

    // Lưu token và thông tin user vào localStorage
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));

    alert("🎉 Đăng ký thành công!");

    // Chuyển đến trang chủ
    router.push("/home");
  } catch (error) {
    alert("❌ " + (error.response?.data?.detail || "Đăng ký thất bại!"));
  }
};

</script>

<style scoped>
.register-page {
  position: relative;
  height: 100vh;
  overflow-x: hidden;
  background-color: #000;
}

.content {
  position: relative;
  z-index: 1;  /* Nằm trên cùng */
  color: white;
  text-align: left;
  padding-top: 10px;
  margin-left: 20px;
}

.auth-form {
      background-color: rgba(255, 255, 255, 0.1); /* Nền trắng trong suốt */
      border-radius: 10px;
      padding: 20px;
      margin: 20px auto;
      width: 700px; /* Chiều rộng khung đăng nhập */
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}
  
.form-group {
  margin-bottom: 15px;
}

.auth-options {
  display: flex;
  align-items: center;
  gap: 10px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
  
input {
  width: 100%;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
}
  
.btn-login {
  width: 100%;
  padding: 10px;
  background-color: #f50057; /* Màu nút đăng nhập */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
  
.btn-login:hover {
  background-color: #c51162; /* Màu nền khi hover */
}

.btn-signup {
  background: none;
  color: #007bff;
  text-decoration: underline;
  cursor: pointer;
}

.signup-link {
  margin-top: 10px;
}

h2 {
  text-align: center;
}

.btn-signin {
  background: none;
  color: #007bff;
  text-decoration: underline;
  cursor: pointer;
}
</style>