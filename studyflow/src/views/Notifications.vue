<template>
  <div class="notification-page">
    
    <!-- Component mạng nơ-ron chồng lên -->
    <NeuralNetworkBg />

    <!-- Content chính -->
    <div class="content">
      <!-- Bên trái -->
      <div class="left">
        <img src="../assets//image/icon.png" alt="logo" class="logo" />
        <h1 style="font-size: 4em;">StudyFlow</h1>
      </div>

      <!-- Giữa -->
      <ul class="nav nav-tabs center-nav">
        <li class="nav-item"><a class="nav-link" href="#" @click="goToHome">Trang chủ</a></li>
        <li class="nav-item"><a class="nav-link" href="#" @click="goToUserStats">Thống kê</a></li>
        <li class="nav-item"><a class="nav-link" href="#" @click="goToTimetable">Thời khóa biểu</a></li>
        <li class="nav-item"><a class="nav-link active" aria-current="page" href="#">Thông báo</a></li>
      </ul>
      
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
                <a href="#" class="btn btn-sm btn-primary w-100 mb-1" @click="goToAccountInformation">Thông tin tài khoản</a>
                <a href="#" class="btn btn-sm btn-outline-danger w-100" @click="logout">Đăng xuất</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notifications List -->
    <div class="notification-box">
      <h2 class="title" style="color: white;">Thông báo học tập</h2>

      <div v-if="notifications.length === 0" class="empty-msg">Không có thông báo nào.</div>
      <ul v-else class="notification-list">
        <li v-for="(note, index) in notifications" :key="index" class="notification-item">
          <div class="time">{{ formatTime(note.timestamp) }}</div>
          <div class="message">{{ note.message }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

const router = useRouter();
const user = ref(null);
const notifications = ref([]);

const dropdownOpen = ref(false)
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

// Lấy thông tin người dùng
const fetchUserProfile = async () => {
  try {
    const token = localStorage.getItem("token"); // Lấy token từ localStorage
    if (!token) {
      throw new Error("Token không tồn tại");
    }

    const response = await fetch("/api/auth/profile", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`, // Gửi token trong header
      },
    });

    console.log("Response từ API:", response); // Debug

    if (!response.ok) {
      throw new Error(`Lỗi HTTP: ${response.status}`);
    }

    const data = await response.json();
    console.log("Thông tin người dùng:", data);
    return data;
  } catch (error) {
    console.error("Lỗi khi lấy thông tin người dùng:", error);
    return null;
  }
};


const fetchNotifications = async () => {
  const token = localStorage.getItem("token");
  if (!token) return;

  const res = await fetch("/api/notifications", {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (res.ok) {
    notifications.value = await res.json();
  } else {
    notifications.value = [];
  }
};

const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" });
};


onMounted(async () => {
  const userData = await fetchUserProfile();
  if (userData) {
    user.value = userData;
  }
  await fetchNotifications();
});

// Chuyển trang Thông tin tài khoản
const goToAccountInformation = () => {
  router.push('/accountinformation');
}

// Chuyển trang Trang chủ
const goToHome = () => {
  router.push('/home');
}

// Chuyển trang Thời khóa biểu
const goToTimetable = () => {
  router.push('/timetable');
}

//Chuyển trang Thống kê
const goToUserStats = () => {
  router.push('/userstats');
}

// Đăng xuất
const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  };
</script>

<style scoped>
.notification-page {
  position: relative;
  height: 100vh;
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
  background-color: rgba(208, 204, 204, 0.844);
  border-radius: 8px;
}

.left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.center-nav {
  display: flex;
  gap: 15px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 1;
  padding-right: 5px;
  gap: 15px;
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

.notification-box {
  position: absolute;
  top: 180px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 30px;
  width: 1100px;
  max-height: 60vh;
  overflow-y: auto;
  z-index: 0;
  text-align: center;
}

.title {
  font-size: 1.8em;
  margin-bottom: 20px;
}

.empty-msg {
  font-size: 1.2em;
  color: #ccc;
}

.notification-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.notification-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 10px;
  text-align: left;
}

.time {
  font-size: 0.9em;
  color: #ccc;
  margin-bottom: 5px;
}

.message {
  font-size: 1.1em;
  font-weight: bold;
  color: white;
}
</style>