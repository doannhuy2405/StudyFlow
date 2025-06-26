<template>
  <div class="home-page">
    
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
      <!-- Bên trái -->
      <div class="left">
        <img src="../assets//image/icon.png" alt="logo" class="logo" />
        <h1 style="font-size: 4em;">StudyFlow</h1>
      </div>

      
      <!-- Phải -->
       <div class="right">
        <div class="dropdown text-end">
          <button
            class="btn p-0 border-0 bg-transparent d-flex align-items-center gap-2"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <!-- Avatar -->
            <img :src= "user?.photo || defaultAvatar" alt="avatar" class="avatar" />
            <!-- Tên hiển thị -->
            <span class="username">{{ user?.fullname }}</span>
          </button>

          <!-- Dropdown nội dung -->
          <div class="dropdown-menu dropdown-menu-end p-2" style="width: 220px;">
            <div class="card border-0 text-center bg-dark text-white">
              <img
                :src= "user?.photo || defaultAvatar"
                class="card-img-top rounded-circle mx-auto mt-2"
                style="width: 60px; height: 60px; object-fit: cover;"
                alt="avatar"
              />
              <div class="card-body p-2">
                <h6 class="card-title mb-1">{{user?.fullname}}</h6>
                <p class="card-text" style="font-size: 0.8em;">{{ user?.email }}</p>
                <a href="#" class="btn btn-sm btn-primary w-100 mb-1" @click="goToHome">Trang chủ</a>
                <a href="#" class="btn btn-sm btn-outline-danger w-100" @click="logout">Đăng xuất</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div v-if="user" style="font-size: 2em; color: white;">
        <p>Xin chào, {{ user.fullname }}!</p>
      </div>

      <div class="auth-form" style="color: white;">
        <h2>Thông tin tài khoản</h2>
          <form @submit.prevent="updateProfile">

          <!-- Thông tin người dùng -->

          <div class="form-group text-center">
            <label for="photo">Ảnh đại diện:</label>
            <input type="file" @change="onFileChange" accept="image/*" />
            <img :src="previewPhoto || user.photo || defaultAvatar" class="avatar-upload-img" />
          </div>

          <div class="form-group">
            <label for="fullname">Họ và tên:</label>
              <input id="fullname" v-model="user.fullname" type="text" disabled readonly style="color: white;" />
            </div>

            <div class="form-group">
              <label for="email">Email:</label>
              <input id="email" v-model="user.email" type="email" required />
            </div>

            <div class="form-group">
              <label for="username">Tên đăng nhập:</label>
              <input type="text" v-model="user.username" id="username" disabled readonly style="color: white;" />
            </div>

            <div class="form-group">
              <label for="password">Mật khẩu:</label>
              <input
                type="password"
                v-model="user.password"
                id="password"
                :placeholder="'Nhập mật khẩu mới.....'"
                autocomplete="off"/>
            </div>

          <!-- Nút cập nhật -->
            <button type="submit" class="btn-update">Cập nhật</button>
            <p>Nếu bạn không có bất kỳ thay đổi gì?</p>
            <button @click="goToHome" class="btn-update">Quay về trang chủ</button>
          </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

const router = useRouter();
const user = ref({
    fullname: "",
    email: "",
    username: "",
    password: "",
});

const dropdownOpen = ref(false)
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

// Avatar
const previewPhoto = ref(null);
let uploadedPhotoBase64 = null;

const onFileChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    previewPhoto.value = reader.result;
    uploadedPhotoBase64 = reader.result;
  };
  reader.readAsDataURL(file);
};


const token = localStorage.getItem("token");

// API lấy thông tin user từ backend
const getUserInfo = async () => {
  try {
    const response = await axios.get("/api/auth/profile", {
      headers: { Authorization: `Bearer ${token}` },
    });

    user.value = response.data;
  } catch (error) {
    console.error("❌ Lỗi lấy thông tin user:", error);
  }
};

// API cập nhật email & password & avatar
const updateProfile = async () => {
  try {
    const response = await axios.get("/api/auth/profile", {
      headers: { Authorization: `Bearer ${token}` },
    });

    const currentUser = response.data;

    const hasEmailChanged = user.value.email !== currentUser.email;
    const hasPasswordChanged = user.value.password !== "";
    const hasPhotoChanged = uploadedPhotoBase64 && uploadedPhotoBase64 !== currentUser.photo;

    if (!hasEmailChanged && !hasPasswordChanged && !hasPhotoChanged) {
      alert("⚠ Không có thay đổi nào để cập nhật!");
      return;
    }

    await axios.put(
      "/api/auth/profile",
      {
        email: user.value.email,
        password: user.value.password,
        photo: hasPhotoChanged ? uploadedPhotoBase64 : null,
      },
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    alert("✅ Cập nhật thành công!");
    user.value.password = "";
    router.push("/home");
  } catch (error) {
    console.error("❌ Lỗi cập nhật:", error);
    alert("⚠ Lỗi khi cập nhật!");
  }
};


onMounted(getUserInfo);


const goToHome = () => {
  router.push('/home');
}


// Đăng xuất
const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  };
</script>

<style scoped>
.home-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background-color: #000;
}

.content {
  position: relative;
  z-index: 1;  /* Nằm trên cùng */
  color: white;
  align-items: center;
  padding-top: 5px;
  display: flex;
  justify-content: space-between;
  gap: 30px;
}


.logo-title {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-title h1 {
  margin: 0px;

}

.logo {
  height: 120px;
}


.nav-tabs {
  display: flex;
  gap: 20px;
  margin-bottom: 0;
  padding-left: 0;
  list-style: none;
}

.nav-link {
  color: white;
  font-weight: bold;
  font-size: 1.1em;
  text-decoration: none;
}

.nav-link:hover {
  background-color: rgba(255,255,255,0.1);
  border-radius: 8px;
}

.left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.center-nav {
  display: flex;
  gap: 25px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 1;
  padding-right: 40px; /* canh khoảng cách với mép phải */
}

 .avatar {
  height: 50px;
  width: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
}

.username {
  font-weight: bold;
  color: white;
  font-size: 1rem;
}

.dropdown-menu {
  z-index: 1000;
  border-radius: 10px;
  overflow: hidden;
}

.auth-form {
      background-color: rgba(255, 255, 255, 0.1); /* Nền trắng trong suốt */
      border-radius: 10px;
      padding: 20px;
      margin: 20px auto;
      width: 750px; /* Chiều rộng khung */
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  }
  
  .form-group {
      margin-bottom: 15px;
  }

  .form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

  .form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

  .avatar-upload {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-upload img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}

input[type="file"] {
  display: block;
  margin: 10px auto;
}

input {
      width: 100%;
      padding: 10px;
      border-radius: 5px;
      border: 1px solid #ccc;
}

.btn-update {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  width: 100%;
}

.btn-update:hover {
  background-color: #0056b3;
}

.main-content {
  margin-top: 20px;
  padding: 20px;
  z-index: 0;
  position: relative;
}

.avatar-upload-img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 50%;
  margin-top: 10px;
}

</style>