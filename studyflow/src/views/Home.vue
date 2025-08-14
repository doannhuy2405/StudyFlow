<!-- eslint-disable vue/multi-word-component-names -->
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
          <li class="nav-item"><a class="nav-link active" aria-current="page" href="#">Trang chủ</a></li>
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
                  <a href="#" class="btn btn-sm btn-outline-danger w-100 logout-btn" @click="logout">Đăng xuất</a>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>

    <!-- Khung tìm kiếm và bộ lọc -->
    <div class="search-filter-container">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Tìm kiếm chủ đề, bài học..." 
          class="search-input"
        >
      <span 
        v-if="searchQuery"
        @click="searchQuery = ''"
        class="clear-search-btn"
        style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); cursor: pointer;"
      > 
      </span>
      </div>
      
      <div class="filter-dropdown">
        <select v-model="filterStatus" class="filter-select">
          <option value="all">Tất cả chủ đề</option>
          <option value="completed">Đã hoàn thành</option>
          <option value="incomplete">Chưa hoàn thành</option>
        </select>
        <i class="fas fa-filter"></i>
      </div>
    </div>


    <!-- Phần thêm chủ đề và danh sách chủ đề -->
    <div class="topic-section">
      <div class="add-topic-container">
        <button class="add-topic-btn" @click="addNewTopic">
          <i class="fas fa-plus-circle"></i> Thêm chủ đề học mới
        </button>

        <button class="add-topic-btn" @click="goToClock">
          <i class="fas fa-plus-circle"></i> Đồng hồ
        </button>
      </div>

      <h2 class="topic-list-title">Danh sách Chủ đề học</h2>

      <div v-if="topics.length === 0" class="empty-topic-message">
        <p>Bạn vẫn chưa có chủ đề học nào! Hãy tạo chủ đề và cùng tôi học nhé!</p>
      </div>

      <div v-for="topic in filteredTopicsWithLessons" :key="topic._id" class="accordion-item bg-dark text-white border-0 mb-4 rounded-lg shadow-md overflow-hidden">
        <div class="accordion-header bg-primary px-4 py-3 cursor-pointer d-flex justify-content-between align-items-center" @click="toggleTopic(topic._id)">
          <h5 class="mb-0 text-white">{{ topic.name }}</h5>
          <span class="text-white">{{ activeTopic === topic._id ? '▲' : '▼' }}</span>
        </div>

        <div v-show="activeTopic === topic._id" class="accordion-body bg-dark p-4" style="color: white;">
          <div v-if="searchQuery && !filteredLessons[topic._id]?.length" class="no-results">
            Không tìm thấy bài học phù hợp với "<strong>{{ searchQuery }}</strong>"
          </div>
          <p style="color: white;">{{ topic.description }}</p>

          <div class="d-flex gap-2 mb-3">
            <button class="btn btn-sm btn-outline-info" @click="editTopic(topic)">Sửa</button>
            <button class="btn btn-sm btn-outline-danger" @click="confirmDeleteTopic(topic.id)">Xóa</button>
            <button class="btn btn-sm btn-outline-success" @click="addLesson(topic.id)">Thêm bài học</button>
          </div>

          <ul class="list-group">
            <li v-for="lesson in filteredLessons[topic._id]" :key="lesson.id" class="lesson-card">
              <div>
                <strong>{{ lesson.name }}</strong>
                <p>{{ lesson.note }}</p>
                <!-- Hiển thị tài liệu nếu có -->
                <div v-if="lesson.documents?.length">
                  <small class="text-info">Tài liệu:</small>
                  <ul>
                    <li v-for="doc in lesson.documents" :key="doc.id">
                      <a :href="`/api/topics/${topic.id}/lessons/${lesson.id}/documents/${doc.id}/preview`"
                        target="_blank" class="text-warning">
                        {{ doc.original_name }}
                      </a>
                      <button class="btn btn-sm btn-outline-danger ms-2" @click="deleteDocument(topic.id, lesson.id, doc.id)">Xóa</button>
                    </li>
                  </ul>
                </div>
                <span class="badge" :class="lesson.status === 'done' ? 'bg-success' : 'bg-warning text-dark'">
                  {{ lesson.status === 'done' ? 'Đã hoàn thành' : 'Chưa hoàn thành' }}
                </span>
              </div>
              <div class="lesson-actions">
                <div class="btn-group">
                  <button type="button" class="btn btn-outline-success dropdown-toggle" data-bs-toggle="dropdown">
                    Trạng thái
                  </button>
                  <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" @click.prevent="changeStatus(lesson, 'done')">Đã hoàn thành</a></li>
                    <li><a class="dropdown-item" href="#" @click.prevent="changeStatus(lesson, 'chưa hoàn thành')">Chưa hoàn thành</a></li>
                  </ul>
                </div>
                <button class="btn btn-outline-info" @click="editLesson(lesson)">Sửa</button>
                <button class="btn btn-outline-danger" @click="deleteLesson(lesson.id, lesson.topic_id)">Xóa</button>
              </div>

              <!-- FORM SỬA BÀI HỌC -->
              <div v-if="editingLessonId === lesson.id" class="mt-3 bg-secondary p-3 rounded">
                <div class="mb-2">
                  <label class="form-label text-white">Tên bài học:</label>
                  <input v-model="editedLesson.name" type="text" class="form-control" />
                </div>
                <div class="mb-2">
                  <label class="form-label text-white">Ghi chú:</label>
                  <input v-model="editedLesson.note" type="text" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label text-white">Ngày học dự kiến:</label>
                  <input v-model="editedLesson.due_date" type="date" class="form-control" />
                </div>
                <div class="mb-3">
                  <label class="form-label text-white">Thêm tài liệu mới (PDF, ảnh...):</label>
                  <input
                    type="file"
                    class="form-control"
                    multiple
                    @change="handleEditFileUpload"
                  />
                  <div v-if="editedFiles.length > 0" class="mt-2">
                    <div v-for="(file, index) in editedFiles" :key="index" class="d-flex align-items-center mb-1">
                      <span class="text-white me-2">{{ file.name }}</span>
                      <button class="btn btn-sm btn-outline-danger" @click="editedFiles.splice(index, 1)">
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn btn-success btn-sm" @click="handleEditLessonSubmit(lesson)">Lưu</button>
                  <button class="btn btn-secondary btn-sm" @click="cancelEditLesson">Hủy</button>
                </div>
              </div>

            </li>
          </ul>

    
          <div v-if="selectedDocumentUrl" class="mt-3">
            <iframe
              :src="selectedDocumentUrl"
              width="100%"
              height="600px"
              style="border: 1px solid #ccc;"
            ></iframe>
          </div>


          <!-- Form thêm bài học -->
          <div v-if="showAddLessonForm === topic._id" class="bg-secondary p-3 rounded mt-3">
            <div class="mb-2">
              <label class="form-label text-white">Tên bài học:</label>
              <input v-model="newLesson.name" type="text" class="form-control" />
            </div>
            <div class="mb-2">
              <label class="form-label">Ghi chú:</label>
              <input v-model="newLesson.note" type="text" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label text-white">Ngày học dự kiến:</label>
              <input v-model="newLesson.due_date" type="date" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label text-white">Tài liệu đính kèm (PDF, hình ảnh...):</label>
              <input 
                type="file" 
                class="form-control" 
                multiple
                @change="handleMultipleFilesUpload"
              />
              <!-- Hiển thị danh sách file đã chọn -->
              <div v-if="selectedFiles.length > 0" class="mt-2">
                <div v-for="(file, index) in selectedFiles" :key="index" class="d-flex align-items-center mb-1">
                  <span class="text-white me-2">{{ file.name }}</span>
                  <button 
                    @click="removeFile(index)"
                    class="btn btn-sm btn-outline-danger"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-success btn-sm" @click="submitNewLesson(topic._id)">Lưu</button>
              <button class="btn btn-secondary btn-sm" @click="cancelAddLesson">Hủy</button>
            </div>
          </div>

          <div v-if="!lessonsMap[topic._id]?.length" class=" mt-3" style="color: white;">Không có bài học nào trong chủ đề này.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import NeuralNetworkBg from '@/components/NeuralNetworkBg.vue';
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import Swal from 'sweetalert2';


// Import avatar mặc đinh hệ thống
import defaultAvatar from '../assets/image/Logo_app.png';

const router = useRouter();
const user = ref(null)
const topics = ref([])
const lessonsMap = ref({})
const activeTopic = ref(null)
const loadingTopics = ref(false)
const loadingLessons = ref({})
// eslint-disable-next-line no-unused-vars
const hasShownReminderPopup = ref(false); 
const selectedDocumentUrl = ref(null)

// Thêm các ref mới
const searchQuery = ref('')
const filterStatus = ref('all') // 'all', 'completed', 'incomplete'


const selectedFiles = ref([])

const editingLessonId = ref(null)
const editedLesson = ref({
  name: '',
  note: '',
  due_date: ''
})
const editedFiles = ref([])

const showAddLessonForm = ref(null)
const newLesson = ref({
  name: '',
  note: '',
  due_date: ''
})

const addLesson = (topicId) => {
  showAddLessonForm.value = topicId
  newLesson.value = {
    name: '',
    note: '',
    due_date: ''
  }
}

const cancelAddLesson = () => {
  showAddLessonForm.value = null
}

// Thêm computed property để lọc chủ đề, bài học
const filteredTopicsWithLessons = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return topics.value.filter(topic => {
    // Lọc theo trạng thái
    let matchesFilter = true;
    if (filterStatus.value !== 'all') {
      const lessons = lessonsMap.value[topic._id] || [];
      const isCompleted = lessons.length > 0 && lessons.every(lesson => lesson.status === 'done');
      matchesFilter = filterStatus.value === 'completed' ? isCompleted : !isCompleted;
    }
    
    if (!query) return matchesFilter;
    
    // Tìm kiếm trong chủ đề
    const topicMatches = topic.name.toLowerCase().includes(query) || 
                        topic.description.toLowerCase().includes(query);
    
    // Tìm kiếm trong bài học
    const lessonMatches = (lessonsMap.value[topic._id] || []).some(lesson => 
      lesson.name.toLowerCase().includes(query) ||
      lesson.note.toLowerCase().includes(query));
    
    return matchesFilter && (topicMatches || lessonMatches);
  });
});

const filteredLessons = computed(() => {
  const query = searchQuery.value.toLowerCase();
  const result = {};
  
  for (const topic of topics.value) {
    const lessons = lessonsMap.value[topic._id] || [];
    result[topic._id] = query 
      ? lessons.filter(lesson => 
          lesson.name.toLowerCase().includes(query) ||
          lesson.note.toLowerCase().includes(query))
      : lessons;
  }
  
  return result;
});

// Xử lý chọn nhiều file
const handleMultipleFilesUpload = (event) => {
  selectedFiles.value = Array.from(event.target.files)
}

// Xóa file khỏi danh sách
const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const submitNewLesson = async (topicId) => {
  if (!newLesson.value.name) {
    alert("Vui lòng điền tên bài học!");
    return;
  }

  try {
    // 1. Tạo bài học
    const res = await fetch(`/api/topics/${topicId}/lessons`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({
        name: newLesson.value.name,
        note: newLesson.value.note,
        due_date: newLesson.value.due_date,
        status: 'not_done'
      })
    });

    if (!res.ok) throw new Error("Lỗi khi thêm bài học!");
    const data = await res.json();
    const lessonId = data.lesson._id;

    // 2. Upload file (nếu có)
    if (selectedFiles.value.length > 0) {
      const formData = new FormData();
      for (const file of selectedFiles.value) {
        formData.append("files", file);
      }

      const uploadRes = await fetch(`/api/topics/${topicId}/lessons/${lessonId}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem("token")}`
        },
        body: formData
      });

      if (!uploadRes.ok) {
        const errorText = await uploadRes.text();
        throw new Error("Upload file thất bại: " + errorText);
      }
    }

    // 3. Cập nhật UI
    await loadLessons(topicId);
    showAddLessonForm.value = null;
    selectedFiles.value = [];
    alert("Thêm bài học và tài liệu thành công!");

  } catch (err) {
    console.error("Lỗi thêm bài học:", err);
    alert("Thêm bài học thất bại: " + err.message);
  }
};

// Hàm mở form sửa bài học
const editLesson = (lesson) => {
  editingLessonId.value = lesson.id
  editedLesson.value = {
    name: lesson.name,
    note: lesson.note,
    due_date: lesson.due_date?.slice(0, 10) || '' 
  }
  editedFiles.value = []
}

const handleEditFileUpload = (event) => {
  editedFiles.value = Array.from(event.target.files)
}

const cancelEditLesson = () => {
  editingLessonId.value = null
  editedLesson.value = {
    name: '',
    note: '',
    due_date: ''
  }
  editedFiles.value = []
}

const handleEditLessonSubmit = async (lesson) => {
  try {
    const updateRes = await fetch(`/api/lessons/${lesson.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: editedLesson.value.name,
        note: editedLesson.value.note,
        due_date: editedLesson.value.due_date + "T00:00:00.000Z"
      })
    })

    if (!updateRes.ok) {
      const error = await updateRes.json()
      alert("Lỗi cập nhật bài học: " + error.detail)
      return
    }

    // Upload file mới nếu có
    if (editedFiles.value.length > 0) {
      const formData = new FormData()
      for (const file of editedFiles.value) {
        formData.append("files", file)
      }

      const uploadRes = await fetch(`/api/topics/${lesson.topic_id}/lessons/${lesson.id}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem("token")}`
        },
        body: formData
      })

      if (!uploadRes.ok) {
        const errText = await uploadRes.text()
        throw new Error("Upload file thất bại: " + errText)
      }
    }

    alert("Cập nhật bài học thành công!")
    await loadLessons(lesson.topic_id)
    cancelEditLesson()
  } catch (err) {
    console.error("Lỗi khi cập nhật bài học:", err)
    alert("Cập nhật thất bại!")
  }
}


const dropdownOpen = ref(false)
// eslint-disable-next-line no-unused-vars
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

// Kiểm tra chủ đề đã hoàn thành
// eslint-disable-next-line no-unused-vars
const isTopicComplete = (topicId) => {
  const lessons = lessonsMap.value[topicId]
  if (!lessons || !lessons.length) return false
  return lessons.every(lesson => lesson.status === 'done')
}

// Toggle mở/đóng chủ đề
const toggleTopic = async (topicId) => {
  if (activeTopic.value === topicId) {
    activeTopic.value = null
  } else {
    activeTopic.value = topicId
    await fetchLessons(topicId)
  }
}

// Lấy danh sách chủ đề từ API
const fetchTopics = async () => {
  loadingTopics.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/topics', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!res.ok) throw new Error('Lỗi khi lấy danh sách chủ đề')
    const data = await res.json()

    topics.value = data.map(topic => ({
      ...topic,
      id: topic._id  
    }))

  } catch (error) {
    console.error('Error fetching topics:', error)
    // eslint-disable-next-line no-undef
    toast.error('Lỗi khi tải danh sách chủ đề')
    topics.value = []
  } finally {
    loadingTopics.value = false
  }
}


// Hàm lấy thông báo mới và hiển thị popup nếu cần
const checkReminderPopup = async () => {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const res = await fetch("/api/notifications", {
      headers: { Authorization: `Bearer ${token}` }
    });

    if (!res.ok) return;

    const notifications = await res.json();
    const latest = notifications?.[0];

    if (!latest || !latest.message.includes("Đã đến giờ học")) return;

    const popupShownKey = "popup_shown_" + new Date().toISOString().slice(0, 10);  // Ví dụ: popup_shown_2025-07-03

    // Nếu popup hôm nay đã hiện rồi thì không hiện lại nữa
    if (localStorage.getItem(popupShownKey)) return;

    // Dù giờ đã qua, miễn là có thông báo "Đã đến giờ học" chưa được hiện hôm nay thì hiện popup
    Swal.fire({
      title: "⏰ Nhắc học",
      text: latest.message,
      icon: "info",
      confirmButtonText: "Bắt đầu học ngay!"
    });

    // Phát âm thanh
    const audio = new Audio("/studyflow/public/That_so_true.mp3");
    audio.play().catch(err => console.warn("Không thể phát âm thanh:", err));

    // Đánh dấu đã hiện
    localStorage.setItem(popupShownKey, "true");

  } catch (err) {
    console.error("Lỗi khi check reminder popup:", err);
  }
};



// Xác nhận xóa chủ đề
const confirmDeleteTopic = async (topicId) => {
  if (confirm('Bạn có chắc muốn xóa chủ đề này? Tất cả bài học trong chủ đề cũng sẽ bị xóa.')) {
    try {
      const token = localStorage.getItem('token')
      const res = await fetch(`/api/topics/${topicId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (!res.ok) throw new Error('Failed to delete topic')
      
      // Cập nhật UI
      topics.value = topics.value.filter(t => t.id !== topicId)
      delete lessonsMap.value[topicId]
      
      if (activeTopic.value === topicId) {
        activeTopic.value = null
      }
      
      // eslint-disable-next-line no-undef
      toast.success('Đã xóa chủ đề thành công')
    } catch (error) {
      console.error('Error deleting topic:', error)
      // eslint-disable-next-line no-undef
      toast.error('Có lỗi khi xóa chủ đề')
    }
  }
}

// Sửa chủ đề
const editTopic = async (topic) => {
  const newName = prompt('Nhập tên mới:', topic.name);
  const newDescription = prompt('Nhập mô tả mới:', topic.description);
  if (newName !== null && newDescription !== null) {
    await fetch(`/api/topics/${topic._id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: newName,
        description: newDescription,
        user_id: topic.user_id, 
      }),
    });
    await fetchTopics();
    lessonsMap.value = {};  

  }
};

// Lấy danh sách bài học của từng topic
const fetchLessons = async (topicId) => {
  if (lessonsMap.value[topicId]) return
  
  loadingLessons.value[topicId] = true
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/topics/${topicId}/lessons`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!res.ok) throw new Error(`Failed to fetch lessons for topic ${topicId}`)
    
    const lessons = await res.json()
    lessonsMap.value = {
      ...lessonsMap.value,
      [topicId]: lessons
    }
  } catch (error) {
    console.error(`Error fetching lessons for topic ${topicId}:`, error)
    // eslint-disable-next-line no-undef
    toast.error('Lỗi khi tải bài học')
    lessonsMap.value[topicId] = []
  } finally {
    loadingLessons.value[topicId] = false
  }
}


// Gọi khi accordion mở ra
watch(topics, () => {
  topics.value.forEach(topic => {
    fetchLessons(topic._id);
  });
});

// Load bài học
const loadLessons = async (topicId) => {
  try {
    const token = localStorage.getItem("token"); // <== THÊM
    const res = await fetch(`/api/topics/${topicId}/lessons`, {
      headers: {
        Authorization: `Bearer ${token}` // <== THÊM
      }
    });

    if (res.ok) {
      const lessons = await res.json();
      lessonsMap.value[topicId] = lessons;
    } else {
      console.error("Không thể tải bài học:", await res.text());
    }
  } catch (err) {
    console.error("Lỗi khi load bài học:", err);
  }
};


// Xóa bài học
const deleteLesson = async (id, topicId) => {
  if (!id || id === 'undefined') {
    alert("ID bài học không hợp lệ!");
    return;
  }

  if (!topicId || topicId === 'undefined') {
    alert("Chủ đề không hợp lệ!");
    return;
  }

  if (confirm("Xóa bài học này?")) {
    try {
      const res = await fetch(`/api/lessons/${id}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        const error = await res.json();
        alert("Lỗi: " + error.detail);
      } else {
        await loadLessons(topicId);
        alert("Xóa bài học thành công!");
      }

    } catch (err) {
      console.error("Lỗi khi xóa bài học:", err);
      alert("Xóa bài học thất bại.");
    }
  }
};


// Trạng thái bài học
// eslint-disable-next-line no-unused-vars
async function toggleStatus(lesson) {
  const newStatus = lesson.status === "Chưa hoàn thành" ? "Đã hoàn thành" : "Chưa hoàn thành"

  const res = await fetch(`/api/lessons/${lesson.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus }),
  })

  const result = await res.json()
  if (res.ok) {
    lesson.status = newStatus
  } else {
    alert("Lỗi cập nhật: " + result.detail)
  }
}

const changeStatus = async (lesson, newStatus) => {
  if (lesson.status === newStatus) return; // Không cần cập nhật nếu không thay đổi

  try {
    const response = await fetch(`/api/lessons/${lesson.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });

    if (response.ok) {
      alert("Cập nhật trạng thái thành công.");
      await loadLessons(lesson.topic_id);  // Cập nhật lại danh sách
    } else {
      const data = await response.json();
      alert(`Lỗi cập nhật trạng thái: ${data.detail}`);
    }
  } catch (err) {
    console.error("Lỗi khi cập nhật trạng thái:", err);
    alert("Có lỗi xảy ra khi cập nhật trạng thái.");
  }
};


const selectedFile = ref(null)

// eslint-disable-next-line no-unused-vars
function handleFileUpload(event) {
  selectedFile.value = event.target.files[0]
}

async function deleteDocument(topicId, lessonId, documentId) {
  if (!confirm("Bạn có chắc muốn xóa tài liệu này không?")) return
  const res = await fetch(`/api/topics/${topicId}/lessons/${lessonId}/documents/${documentId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`
    }
  })
  if (res.ok) {
    alert("Đã xóa tài liệu")
    await loadLessons(topicId)
  } else {
    alert("Xóa thất bại")
  }
}


onMounted(async () => {
  const userData = await fetchUserProfile();
  if (userData) {
    user.value = userData;
    await fetchTopics(); 
    await checkReminderPopup();
  }
});

// Chuyển trang Thông tin tài khoản
const goToAccountInformation = () => {
  router.push('/accountinformation');
}

// Chuyển trang Thời khóa biểu
const goToTimetable = () => {
  router.push('/timetable');
}

//Chuyển trang Thông báo
const goToNotifications = () => {
  router.push('/notifications');
}

//Chuyển trang Thống kê
const goToUserStats = () => {
  router.push('/userstats');
}

//Chuyển trang Thêm chủ đề
const addNewTopic = () => {
  router.push('/addtopic');
}

// Chuyển trang Đồng hồ
const goToClock = () => {
  router.push('/clock'); 
};


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

/* Phần topic section mới */
.topic-section {
  position: relative;
  z-index: 0;
  margin-top: 30px;
  padding: 0 40px;
  width: 95%;
}

.add-topic-container {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-start;
  padding-left: 0;
  gap: 30px;
}

.add-topic-btn {
  background-color: rgba(255, 255, 255, 0.08);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  border: 1px solid white;
}

.add-topic-btn:hover {
  background-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(112, 112, 112, 0.186)
}

.add-topic-btn i {
  font-size: 1.3rem;
}

.topic-list-title {
  color: white;
  font-size: 1.3em;
  margin-bottom: 20px;
  text-align: left;
  padding-left: 10px;
}


.empty-topic-message {
  text-align: center;
  color: white;
  font-size: 1.2rem;
  padding: 40px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  margin-left: -5px; 
  margin-right: -5px;
}


.topic-section {
  width: 100%;
  padding: 10px 40px;
  margin-top: 30px;
  margin-left: 0;
  margin-right: 0;
}

.topic-list-title {
  color: #fff;
  margin: 1.5rem 0;
  font-size: 1.8rem;
  text-align: center;
}


.accordion-header {
  background-color: #1a1f3c;
  cursor: pointer;
  transition: background 0.3s ease;
  border-radius: 8px 8px 0 0;
}

.accordion-header:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.accordion-body {
  background-color: #20283e;
  border-radius: 0 0 8px 8px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}

.lesson-card {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 15px;
  margin-bottom: 10px;
  color: #fff;
}

.lesson-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.bg-primary {
  --bs-bg-opacity: 1;
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.search-filter-container {
  display: flex;
  gap: 15px;
  margin: 20px 0;
  padding: 0 15px;
  align-items: center;
  flex-wrap: nowrap; /* Đổi từ wrap sang nowrap */
  width: 100%;
  position: relative; /* Thêm position relative */
}

.search-box {
  position: relative;
  flex-grow: 2; /* Tăng flex-grow để chiếm nhiều không gian hơn */
  width: 80%; /* Chiếm 200% width */
  max-width: none; /* Bỏ max-width cũ */
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #aaa;
}

.search-input {
  width: 82%;
  padding: 10px 15px 10px 40px;
  border: 1px solid #444;
  border-radius: 30px;
  background-color: #2a2a2a;
  color: white;
  font-size: 14px;
  transition: all 0.3s ease;
}

.filter-dropdown {
  position: absolute; /* Đổi thành absolute */
  right: 15px; /* Đẩy sang bên phải */
  top: 50%;
  transform: translateY(-50%);
  z-index: 1; /* Đảm bảo nằm trên các phần tử khác */
}

.filter-dropdown i {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #aaa;
  pointer-events: none;
}

.filter-select {
  padding: 10px 35px 10px 15px;
  border: 1px solid #444;
  border-radius: 30px;
  background-color: #2a2a2a;
  color: white;
  font-size: 14px;
  appearance: none;
  cursor: pointer;
  min-width: 200px;
}

/* Responsive */
@media (max-width: 768px) {
  .search-filter-container {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .search-box {
    width: 100%;
  }
  
  .filter-dropdown {
    position: relative;
    right: auto;
    top: auto;
    transform: none;
    align-self: flex-end;
  }
}

.no-results {
  color: #aaa;
  padding: 10px;
  text-align: center;
  font-style: italic;
}

.no-results strong {
  color: #fff;
  font-style: normal;
}


.clear-search-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  padding: 0 5px;
}

.clear-search-btn:hover {
  color: #fff;
}

.search-input {
  padding-right: 35px;
}

</style>