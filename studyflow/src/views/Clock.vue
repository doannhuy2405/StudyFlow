<template>
  <div class="clock-page">
    
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
        <li class="nav-item"><a class="nav-link" href="#" @click="goToNotifications">Thông báo</a></li>
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
    
      <!-- Nút bắt đầu học -->
    <div class="header">
      <div class="timer-buttons">
        <button class="btn btn-outline-warning" @click="startStudyMode">
          <i class="fas fa-play-circle"></i> Bắt đầu học
        </button>
        <button class="btn btn-outline-success" @click="startPomodoroMode">
          <i class="fas fa-stopwatch"></i> Pomodoro 50'
        </button>
      </div>
    </div>

    <!-- Giao diện toàn màn hình khi đang học -->
    <div v-if="timerStore.isTracking" class="fullscreen-overlay">
      <div class="timer-box">
        <h2>Đang học</h2>
        <h1>{{ timerStore.formattedElapsed }}</h1>

        <div class="d-flex justify-content-center gap-3 mt-4">
          <button class="btn btn-danger" @click="stopTracking">Dừng</button>
          <button class="btn btn-outline-light" @click="goToHome">Về trang chủ</button>
        </div>
      </div>
    </div>


    <!-- Giao diện toàn màn hình cho Pomodoro -->
    <div v-if="timerStore.isPomodoro" class="fullscreen-overlay pomodoro">
      <div class="timer-box">
        <h2>Pomodoro</h2>
        <h1>{{ timerStore.formattedCountdown }}</h1>
        <button class="btn btn-warning mt-4" @click="stopPomodoro">Dừng Pomodoro</button>
      </div>
    </div>

    <!-- Lịch sử học tập -->
    <div class="history-container" v-if="filteredStudyHistory.length > 0">
      <h2>Lịch sử học tập</h2>
      <table class="table table-dark table-bordered mt-3">
        <thead>
          <tr>
            <th>Ngày</th>
            <th>Bắt đầu</th>
            <th>Kết thúc</th>
            <th>Thời lượng (phút)</th>
            <th>Loại học</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(session, index) in filteredStudyHistory" :key="index">
            <td>{{ formatDate(session.start) }}</td>
            <td>{{ formatTime(session.start) }}</td>
            <td>{{ formatTime(session.end) }}</td>
            <td>{{ session.duration ? (Number(session.duration) / 60).toFixed(1) : '—' }}</td>
            <td>{{ session.type === 'pomodoro' ? 'Pomodoro' : 'Đếm giờ' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTimerStore } from '@/stores/timerStore';

// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

const router = useRouter();
const user = ref(null);
const studyHistory = ref([])
const timerStore = useTimerStore()

let timerInterval = null
const elapsedSeconds = ref(0)
const countdownSeconds = ref(25 * 60)

const filteredStudyHistory = computed(() => {
  return studyHistory.value.filter(s => s.start && s.end && s.duration);
});


const startStudyMode = async () => {
  const token = localStorage.getItem("token")
  const res = await fetch("/api/timetracking/start", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    }
  })

  if (res.ok) {
    timerStore.startTracking()
  } else {
    alert("Không thể bắt đầu học.")
  }
}

const startPomodoroMode = async () => {
  const token = localStorage.getItem("token")
  const res = await fetch("/api/pomodoro/start", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    }
  })

  if (res.ok) {
    timerStore.startPomodoro()
  } else {
    alert("Không thể bắt đầu Pomodoro.")
  }
}


// Hiển thị theo múi giờ Việt Nam (Asia/Ho_Chi_Minh)
const formatDate = (isoString) => {
  return new Intl.DateTimeFormat('vi-VN', {
    timeZone: 'Asia/Ho_Chi_Minh',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(isoString));
};

const formatTime = (isoString) => {
  return new Intl.DateTimeFormat('vi-VN', {
    timeZone: 'Asia/Ho_Chi_Minh',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).format(new Date(isoString));
};


const dropdownOpen = ref(false)
function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

// Format thời gian đếm lên
const formattedElapsed = computed(() => {
  const hours = Math.floor(elapsedSeconds.value / 3600);
  const minutes = Math.floor((elapsedSeconds.value % 3600) / 60);
  const seconds = elapsedSeconds.value % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  } else {
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
  }
});

// Tăng mỗi giây khi học
watch(() => timerStore.isTracking, (isNowTracking) => {
  if (isNowTracking) {
    elapsedSeconds.value = 0;

    timerInterval = setInterval(() => {
      elapsedSeconds.value++;
    }, 1000);
  } else {
    clearInterval(timerInterval);
    timerInterval = null;
  }
});


// Format Pomodoro
const formattedCountdown = computed(() => {
  const m = String(Math.floor(countdownSeconds.value / 60)).padStart(2, '0');
  const s = String(countdownSeconds.value % 60).padStart(2, '0');
  return `${m}:${s}`;
});

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


// Dừng học
const stopTracking = async () => {
  try {
    const token = localStorage.getItem("token");
    // Gọi API để dừng tracking trước
    const res = await fetch("/api/timetracking/stop", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (res.ok) {
      // Sau khi API thành công mới dừng store
      await timerStore.stopTracking();
      
      await fetchStudyHistory(); // Cập nhật lại lịch sử
    } else {
      const error = await res.json();
      alert(`Lỗi khi dừng: ${error.message || 'Không thể dừng session'}`);
    }
  } catch (err) {
    console.error("Lỗi khi dừng:", err);
    alert("Có lỗi xảy ra khi dừng session");
  }
};


const stopPomodoro = async () => {
  try {
    const token = localStorage.getItem("token");
    // Gọi API để dừng pomodoro
    const res = await fetch("/api/pomodoro/stop", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (res.ok) {
      await timerStore.stopPomodoro();
      await fetchStudyHistory(); // Cập nhật lại lịch sử
    } else {
      const error = await res.json();
      alert(`Lỗi khi dừng Pomodoro: ${error.message || 'Lỗi không xác định'}`);
    }
  } catch (err) {
    console.error("Lỗi khi dừng Pomodoro:", err);
    alert("Có lỗi xảy ra khi dừng Pomodoro");
  }
};


// Lịch sử học tập
const fetchStudyHistory = async () => {
  const token = localStorage.getItem("token"); // 🟢 Lấy token từ localStorage
  if (!token) {
    console.error("Không có token, người dùng chưa đăng nhập.");
    return;
  }

  try {
    const res = await fetch("/api/timetracking/history", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`, // 🟢 Gửi token vào header
      }
    });
    

    if (!res.ok) throw new Error("Không thể lấy lịch sử học tập");
    const data = await res.json();
    studyHistory.value = data;
  } catch (err) {
    console.error("Lỗi lấy lịch sử học:", err);
  }
};


onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval);
  }
});

// Mounted
onMounted(async () => {
  const userData = await fetchUserProfile();
  if (userData) {
    user.value = userData;
    await fetchStudyHistory();
  }
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

//Chuyển trang Thông báo
const goToNotifications = () => {
  router.push('/notifications');
}

// Đăng xuất
const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/");
  };
</script>

<style scoped>
.clock-page {
  position: relative;
  height: 100vh;
  overflow-x: hidden;
  background-color: #000;
  text-align: center;
}

.content {
  position: relative;
  z-index: 1;  
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

.fullscreen-overlay {
  position: fixed;
  inset: 0;
  background: black;
  color: white;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.header {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 50px;
}

.timer-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin: 30px 0;
  z-index: 0;
}

.fullscreen-overlay {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #000000, #0a0a0a);
  color: white;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pomodoro {
  background: radial-gradient(circle, #004d00, #000000);
}

.timer-box {
  text-align: center;
  padding: 40px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  box-shadow: 0 0 20px rgba(0,255,255,0.4);
}

.timer-box h1 {
  font-size: 6rem;
  margin-bottom: 20px;
}

.timer-box h2 {
  font-size: 2rem;
  margin-bottom: 10px;
}

.history-container {
  position: relative;
  z-index: 0;
  color: white;
  padding: 20px;
}

</style>