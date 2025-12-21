WITH src(code, name, faculty_name) AS (
  VALUES
  ('BIO1','Công nghệ sinh học','Khoa Công nghệ sinh học, Hóa học và Kỹ thuật môi trường'),
  ('CHE1','Kỹ thuật hóa học','Khoa Công nghệ sinh học, Hóa học và Kỹ thuật môi trường'),

  ('EEE1','Kỹ thuật điều khiển và tự động hóa','Khoa Điện - Điện tử'),
  ('EEE-AI','Kỹ thuật điều khiển và tự động hóa (Robot và trí tuệ nhân tạo)','Khoa Điện - Điện tử'),
  ('EEE2','Kỹ thuật y sinh (Điện tử y sinh)','Khoa Điện - Điện tử'),
  ('EEE3','Kỹ thuật Điện tử - Viễn thông (Hệ thống nhúng thông minh và IoT)','Khoa Điện - Điện tử'),
  ('EEE4','Kỹ thuật Điện tử - Viễn thông (Thiết kế vi mạch bán dẫn)','Khoa Điện - Điện tử'),

  ('MEM1','Kỹ thuật cơ điện tử','Khoa Cơ khí - Cơ điện tử'),
  ('MEM1-IMS','Hệ thống cơ điện tử thông minh (Các học phần chuyên ngành học bằng tiếng Anh)','Khoa Cơ khí - Cơ điện tử'),
  ('MEM2','Kỹ thuật cơ khí','Khoa Cơ khí - Cơ điện tử'),

  ('MSE1','Vật liệu tiên tiến và Công nghệ nano','Khoa Khoa học và Kỹ thuật vật liệu'),
  ('MSE-AI','Vật liệu thông minh và trí tuệ nhân tạo','Khoa Khoa học và Kỹ thuật vật liệu'),
  ('MSE-IC','Chip bán dẫn và Công nghệ đóng gói','Khoa Khoa học và Kỹ thuật vật liệu'),

  ('VEE1','Kỹ thuật ô tô','Khoa Kỹ thuật Ô tô và Năng lượng'),
  ('VEE2','Cơ điện tử ô tô','Khoa Kỹ thuật Ô tô và Năng lượng'),
  ('VEE3','Kỹ thuật phần mềm ô tô','Khoa Kỹ thuật Ô tô và Năng lượng'),

  ('ICT1','Công nghệ thông tin','Khoa Hệ thống thông tin'),
  ('ICT2','Kỹ thuật phần mềm (Một số học phần chuyên ngành học bằng tiếng Anh)','Khoa Hệ thống thông tin'),
  ('ICT4','An toàn thông tin (Một số học phần chuyên ngành học bằng tiếng Anh)','Khoa Hệ thống thông tin'),
  ('ICT-VJ','Công nghệ thông tin Việt Nhật','Khoa Hệ thống thông tin'),
  
  ('ICT3','Khoa học máy tính (Trí tuệ nhân tạo và Khoa học dữ liệu)','Khoa Trí tuệ nhân tạo'),
  ('ICT5','Trí tuệ nhân tạo','Khoa Trí tuệ nhân tạo'),
  
  ('ICT-TN','Tài năng Khoa học máy tính','Khoa Khoa học máy tính'),
  
  ('FBE1','Quản trị kinh doanh','Khoa Quản trị kinh doanh'),
  ('FBE4','Quản trị nhân lực','Khoa Quản trị kinh doanh'),
  
  ('FBE6','Kinh doanh quốc tế (Các học phần chuyên ngành học bằng tiếng Anh)','Khoa Kinh tế và Kinh doanh quốc tế'),
  ('FBE7','Logistics và Quản lý chuỗi cung ứng (Một số học phần chuyên ngành học bằng tiếng Anh)','Khoa Kinh tế và Kinh doanh quốc tế'),
  ('FBE8','Marketing (Một số học phần chuyên ngành học bằng tiếng Anh)','Khoa Kinh tế và Kinh doanh quốc tế'),
  
  ('FBE2','Kế toán','Khoa Tài chính - Kế toán'),
  ('FBE3','Tài chính - Ngân hàng','Khoa Tài chính - Kế toán'),
  ('FBE5','Kiểm toán','Khoa Tài chính - Kế toán'),

  ('FTS1','Du lịch (Định hướng Quản trị du lịch)','Khoa Du lịch - Khách sạn'),
  ('FTS2','Quản trị khách sạn','Khoa Du lịch - Khách sạn'),
  ('FTS3','Kinh doanh Du lịch số','Khoa Du lịch - Khách sạn'),
  ('FTS4','Hướng dẫn Du lịch quốc tế','Khoa Du lịch - Khách sạn'),

  ('FIDT1','Kinh tế số','Khoa Công nghệ số liên ngành'),
  ('FIDT2','Quản trị kinh doanh (Kinh doanh số)','Khoa Công nghệ số liên ngành'),
  ('FIDT3','Thương mại điện tử','Khoa Công nghệ số liên ngành'),
  ('FIDT4','Logistics và Quản lý chuỗi cung ứng (Logistics số)','Khoa Công nghệ số liên ngành'),
  ('FIDT5','Marketing (Công nghệ Marketing)','Khoa Công nghệ số liên ngành'),
  ('FIDT6','Truyền thông đa phương tiện','Khoa Công nghệ số liên ngành'),
  ('FIDT7','Công nghệ tài chính','Khoa Công nghệ số liên ngành'),

  ('FLE1','Ngôn ngữ Anh','Khoa Ngôn ngữ Anh'),
  ('FLC1','Ngôn ngữ Trung Quốc','Khoa Ngôn ngữ Trung Quốc'),
  ('FLJ1','Ngôn ngữ Nhật','Khoa Ngôn ngữ Nhật Bản'),
  ('FLF1','Ngôn ngữ Pháp','Khoa Ngôn ngữ Pháp'),
  ('FLK1','Ngôn ngữ Hàn Quốc','Khoa Ngôn ngữ Hàn Quốc'),
  ('FOS1','Đông phương học','Khoa Đông phương học'),
  
  ('MED1','Y khoa','Khoa Y'),
  
  ('FTME','Y học cổ truyền','Khoa Y học cổ truyền'),

  ('NUR1','Điều dưỡng','Khoa Điều dưỡng'),
  ('MIW','Hộ sinh','Khoa Điều dưỡng'),
  
  ('HM1','Quản lý bệnh viện','Khoa Y tế công cộng'),
  
  ('DEN1','Răng - Hàm - Mặt','Khoa Răng Hàm Mặt'),
  
  ('PHA1','Dược học','Khoa Dược'),

  ('MTT1','Kỹ thuật xét nghiệm y học','Khoa Kỹ thuật Y học'),
  ('RET1','Kỹ thuật phục hồi chức năng','Khoa Kỹ thuật Y học'),
  ('RTS1','Kỹ thuật hình ảnh y học','Khoa Kỹ thuật Y học'),

  ('BMS','Khoa học y sinh','Khoa Khoa học Y sinh'),

  ('FOL1','Luật kinh tế','Khoa Luật'),
  ('FOL2','Luật kinh doanh','Khoa Luật'),
  ('FOL3','Luật','Khoa Luật'),
  ('FOL4','Luật quốc tế','Khoa Luật'),
  ('FOL5','Luật thương mại quốc tế','Khoa Luật'),
  
  ('FSP1','Vật lý tài năng','Khoa Khoa học cơ bản')
  
)
INSERT INTO miscore_major (code, name, faculty_id, school_id, is_active, created_at, updated_at)
SELECT s.code, s.name, f.id, f.school_id, TRUE, now(), now()
FROM src s
JOIN miscore_faculty f ON f.name = s.faculty_name
ON CONFLICT (code) DO UPDATE
SET name       = EXCLUDED.name,
    faculty_id = EXCLUDED.faculty_id,
    school_id  = EXCLUDED.school_id,
    updated_at = now();