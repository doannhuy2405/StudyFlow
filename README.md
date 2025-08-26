# StudyFlow - Hướng Dẫn Cài Đặt & Chạy Dự Án
Hướng dẫn này sẽ giúp bạn cài đặt và chạy dự án StudyFlow trên môi trường local.

# 1.  Điều Kiện Tiên Quyết
Trước khi bắt đầu, hãy đảm bảo máy bạn đã cài đặt:

Node.js (version 18.x trở lên)

npm hoặc yarn hoặc pnpm (package manager)

Python (version 3.9 trở lên)

MongoDB (local hoặc MongoDB Atlas)

# 2. Cài Đặt & Chạy Frontend (Vue.js + Vite)
  2.1. Clone repository
    bash
    git clone <your-repo-url>
    cd studyflow-frontend
   
   2.2. Cài đặt dependencies
    Sử dụng npm (hoặc yarn/pnpm):
    bash
    npm install
   
  2.3. Cấu hình biến môi trường
    Tạo file .env trong thư mục frontend và thêm:
    env
    VITE_API_BASE_URL=http://localhost:8000
    
  2.4. Chạy ứng dụng ở chế độ development
    bash
    npm run dev
    Ứng dụng sẽ chạy tại: http://localhost:5173
    
  2.5. Build cho production
    bash
    npm run build
   
# 3. Cài Đặt & Chạy Backend (FastAPI)
  3.1. Vào thư mục backend
    bash
    cd backend
   
  3.2. Tạo virtual environment (khuyến nghị)
    bash
    python -m venv venv
    
  2.3. Kích hoạt virtual environment
    Trên Windows:
    bash
    venv\Scripts\activate
    Trên macOS/Linux:
    bash
    source venv/bin/activate
  
  3.4. Cài đặt dependencies
    bash
    pip install -r requirements.txt
    
  3.5. Cấu hình biến môi trường
    Tạo file .env trong thư mục backend và thêm:
    env
    MONGODB_URI=mongodb://localhost:27017/studyflow
    JWT_SECRET_KEY=your-super-secret-key-here
    
  3.6. Chạy server
    bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    API sẽ chạy tại: http://localhost:8000
    Documentation API: http://localhost:8000/docs

# 4. Triển Khai Production
Frontend (Vite)
bash
npm run build
File build sẽ được tạo trong thư mục dist/

Backend (FastAPI)
Sử dụng Uvicorn với worker:

bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 5. Xử Lý Lỗi Thường Gặp
Lỗi CORS: Đảm bảo backend đã cấu hình CORS cho frontend URL

Lỗi kết nối MongoDB: Kiểm tra MongoDB đang chạy và connection string

Lỗi dependencies: Xóa thư mục node_modules và chạy npm install lại

# Hỗ Trợ
Nếu có bất kỳ vấn đề gì trong quá trình cài đặt, vui lòng liên hệ:
Tên: Đoàn Thị Như Ý
Email: doannhuy2405@gmail.com
