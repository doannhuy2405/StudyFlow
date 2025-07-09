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

      <!-- Giữa -->
      <ul class="nav nav-tabs center-nav">
        <li class="nav-item"><a class="nav-link" href="#" @click="goToHome">Trang chủ</a></li>
        <li class="nav-item"><a class="nav-link" href="#" @click="goToUserStats">Thống kê</a></li>
        <li class="nav-item"><a class="nav-link active" aria-current="page" href="#">Thời khóa biểu</a></li>
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

    <div class="schedule-container">
      <h2 class="schedule-title">Thời khóa biểu học tập</h2>
      
      <!-- Lọc theo tuần/tháng -->
      <div class="schedule-filter">
        <button 
          @click="setTimeRange('week')" 
          :class="{ active: timeRange === 'week' }"
        >
          Tuần này
        </button>
        <button 
          @click="setTimeRange('month')" 
          :class="{ active: timeRange === 'month' }"
        >
          Tháng này
        </button>
      </div>
      
      <!-- Hiển thị thời khóa biểu -->
      <div class="schedule-grid">
        <div 
          v-for="day in days" 
          :key="day.date" 
          class="schedule-day"
          :class="{ 'today': day.isToday }"
        >
          <div class="day-header">
            <div class="day-name">{{ day.dayName }}</div>
            <div class="day-date">{{ formatDate(day.dateObj) }}</div>
          </div>
          
          <div class="lessons-list">
            <div 
              v-for="lesson in day.lessons" 
              :key="lesson._id" 
              class="lesson-item"
              :class="{
                'done': lesson.status === 'done',
                'not-done': lesson.status === 'not_done',
                'in-progress': lesson.status === 'in_progress'
              }"
            >
              <div class="lesson-time">{{ formatTime(lesson.due_date) }}</div>
              <div class="lesson-info">
                <h4 class="lesson-title">{{ lesson.name }}</h4>
                <p class="lesson-topic">{{ getTopicName(lesson.topic_id) }}</p>
                <p class="lesson-note" v-if="lesson.note">{{ lesson.note }}</p>
              </div>
              <div class="lesson-status">
                <span v-if="lesson.status === 'done'">✓</span>
                <span v-else-if="lesson.status === 'in_progress'">⌛</span>
              </div>
            </div>
            
            <div v-if="day.lessons.length === 0" class="no-lessons">
              Không có bài học nào
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';

// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

const router = useRouter();
const user = ref(null);
const lessons = ref([]);
const topics = ref([]);
const timeRange = ref('week');

const formatDate = (date) => {
  return date.toLocaleDateString('vi-VN'); 
};


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


// Lấy danh sách bài học có due_date
const fetchLessons = async () => {
  try {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("Token không tồn tại");

    const response = await fetch("/api/lessons", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) throw new Error(`Lỗi HTTP: ${response.status}`);
    
    const data = await response.json();
    return data.filter(lesson => lesson.due_date); // Chỉ lấy bài học có due_date
  } catch (error) {
    console.error("Lỗi khi lấy danh sách bài học:", error);
    return [];
  }
};

// Lấy danh sách chủ đề
const fetchTopics = async () => {
  try {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("Token không tồn tại");

    const response = await fetch("/api/topics", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) throw new Error(`Lỗi HTTP: ${response.status}`);
    
    return await response.json();
  } catch (error) {
    console.error("Lỗi khi lấy danh sách chủ đề:", error);
    return [];
  }
};


// Parse chuỗi ngày theo múi giờ địa phương (tránh bị lệch)
const parseLocalDate = (dateStr) => {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day); 
};


// Hàm chuyển đổi thời gian
const formatTime = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
};

// Hàm lấy tên chủ đề từ topic_id
const getTopicName = (topicId) => {
  const topic = topics.value.find(t => t._id === topicId);
  return topic ? topic.name : 'Không có chủ đề';
};

// Thiết lập phạm vi thời gian
const setTimeRange = (range) => {
  timeRange.value = range;
};

// Tính toán các ngày trong tuần/tháng hiện tại
const days = computed(() => {
  const now = new Date();
  const startDate = new Date(now);
  const endDate = new Date(now);
  
  if (timeRange.value === 'week') {
    // Bắt đầu từ thứ 2
    startDate.setDate(now.getDate() - now.getDay() + (now.getDay() === 0 ? -6 : 1));
    endDate.setDate(startDate.getDate() + 6);
  } else {
    // Tháng này
    startDate.setDate(1);
    endDate.setMonth(startDate.getMonth() + 1);
    endDate.setDate(0);
  }
  
  const daysArray = [];
  const currentDate = new Date(startDate);
  
  while (currentDate <= endDate) {
    const dateStr = currentDate.toISOString().split('T')[0];
    const dayLessons = lessons.value.filter(lesson => {
      const lessonDate = parseLocalDate(lesson.due_date.split('T')[0]);
      return lessonDate.toDateString() === currentDate.toDateString();
    });
    
    daysArray.push({
      date: currentDate.toLocaleDateString('vi-VN', { day: 'numeric', month: 'numeric' }),
      dayName: currentDate.toLocaleDateString('vi-VN', { weekday: 'long' }),
      dateObj: new Date(currentDate),
      isToday: currentDate.toDateString() === now.toDateString(),
      lessons: dayLessons
    });
    
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return daysArray;
});


onMounted(async () => {
  const userData = await fetchUserProfile();
  if (userData) {
    user.value = userData;
  }

  lessons.value = await fetchLessons();
  topics.value = await fetchTopics();
});


//Chuyển trang Thông báo
const goToNotifications = () => {
  router.push('/notifications');
}

// Chuyển trang Thông tin tài khoản
const goToAccountInformation = () => {
  router.push('/accountinformation');
}

// Chuyển trang Trang chủ
const goToHome = () => {
  router.push('/home');
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
.home-page {
  position: relative;
  height: 100vh;
  overflow-x: hidden;
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
  padding-right: 5px; /* canh khoảng cách với mép phải */
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

.schedule-container {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
  position: relative;
  z-index: 0;
  color: white;
}

.schedule-title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 2.5em;
  color: #fff;
}

.schedule-filter {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.schedule-filter button {
  padding: 8px 20px;
  border: none;
  border-radius: 20px;
  background-color: #333;
  color: white;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
}

.schedule-filter button.active {
  background-color: #4CAF50;
}

.schedule-filter button:hover {
  background-color: #555;
}

.schedule-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 15px;
}

.schedule-day {
  background-color: rgba(30, 30, 30, 0.8);
  border-radius: 10px;
  padding: 15px;
  min-height: 300px;
}

.schedule-day.today {
  border: 2px solid #4CAF50;
  background-color: rgba(30, 30, 30, 0.9);
}

.day-header {
  text-align: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #444;
}

.day-name {
  font-weight: bold;
  font-size: 1.1em;
  color: #4CAF50;
}

.day-date {
  font-size: 0.9em;
  color: #aaa;
}

.lessons-list {
  height: calc(100% - 50px);
  overflow-y: auto;
}

.lesson-item {
  background-color: rgba(50, 50, 50, 0.6);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
}

.lesson-item.done {
  opacity: 0.7;
  border-left: 4px solid #4CAF50;
}

.lesson-item.not-done {
  border-left: 4px solid #f44336;
}

.lesson-item.in-progress {
  border-left: 4px solid #FFC107;
}

.lesson-time {
  font-size: 0.8em;
  color: #aaa;
  margin-bottom: 5px;
}

.lesson-info {
  flex-grow: 1;
}

.lesson-title {
  margin: 0 0 5px 0;
  font-size: 1em;
}

.lesson-topic {
  margin: 0;
  font-size: 0.8em;
  color: #888;
}

.lesson-note {
  margin: 5px 0 0 0;
  font-size: 0.8em;
  color: #bbb;
  font-style: italic;
}

.lesson-status {
  text-align: right;
  font-size: 1.2em;
}

.no-lessons {
  text-align: center;
  color: #666;
  font-size: 0.9em;
  padding: 20px 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .schedule-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 900px) {
  .schedule-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 600px) {
  .schedule-grid {
    grid-template-columns: 1fr;
  }
}

</style>