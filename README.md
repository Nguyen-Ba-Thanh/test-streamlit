# Demo tách giọng hát khỏi nhạc nền bằng Demucs

Ứng dụng web nhỏ dùng **Python + Streamlit + Demucs (mô hình HTDemucs)**. Người dùng tải lên một file âm thanh có giọng hát và nhạc đệm; ứng dụng tạo hai file WAV:

- `*_vocals.wav`: phần giọng hát được mô hình ước lượng.
- `*_instrumental.wav`: phần nhạc nền còn lại (Demucs đặt tên nội bộ là `no_vocals.wav`).

> Đây là công cụ tách nguồn âm thanh (audio source separation), không phải công cụ nhận diện lời hát hay chấm điểm giọng hát. Kết quả AI có thể còn lẫn âm thanh từ nguồn kia.

## 1. Mục tiêu và phạm vi

**Đầu vào:** một đoạn hát có nhạc, định dạng MP3, WAV, FLAC, OGG hoặc M4A.

**Xử lý:** Demucs phân tích tín hiệu và ước lượng nguồn vocal, sau đó tạo phần âm thanh còn lại.

**Đầu ra:** hai file WAV để nghe trực tiếp hoặc tải về.

**Giao diện:** Streamlit cung cấp vùng tải file, nút chạy xử lý, trình phát âm thanh và nút tải kết quả. Streamlit không tự tách âm thanh; nó chỉ là giao diện gọi chương trình Demucs.

## 2. Demucs là gì?

Demucs là hệ thống học sâu cho bài toán **music source separation** — tách các nguồn âm thanh đã bị trộn với nhau trong bản nhạc. Mô hình được huấn luyện trên nhiều ví dụ âm thanh để học đặc trưng của từng nguồn, thay vì chỉ lọc theo một dải tần số cố định.

Bản phối có thể được biểu diễn khái quát:

`Mixture ≈ Vocal + Drums + Bass + Other instruments`

Trong chế độ `--two-stems=vocals`, Demucs tạo hai nhóm:

`Mixture ≈ Vocal + No-vocals`

- `vocals`: nguồn giọng hát được mô hình ước lượng.
- `no_vocals`: phần nhạc còn lại được ước lượng sau khi tách vocal.

Đây là cách giải thích trực quan; quá trình nội bộ của mô hình phức tạp hơn phép cộng đơn giản này.

### HTDemucs

HTDemucs là một mô hình thuộc họ Hybrid Transformer Demucs. Mô hình kết hợp xử lý biểu diễn âm thanh ở miền thời gian và miền tần số, đồng thời dùng kiến trúc học sâu để tận dụng thông tin ngữ cảnh của bản nhạc. Ứng dụng này gọi mô hình bằng lệnh `-n htdemucs`.

### Demucs và Spleeter khác nhau thế nào?

| Tiêu chí | Demucs / HTDemucs | Spleeter |
|---|---|---|
| Bản chất | Mô hình học sâu cho tách nguồn âm thanh | Bộ công cụ tách nguồn âm thanh dựa trên mạng nơ-ron |
| Đầu ra | Có thể tách 2 nguồn hoặc nhiều stem tùy chế độ | Có các cấu hình 2, 4 hoặc 5 stems tùy mô hình |
| Trong demo này | Chọn chế độ vocal / no-vocals | Không dùng trực tiếp |
| Lựa chọn thực tế | Phù hợp với demo hiện tại; cần kiểm tra tài nguyên máy | Có thể làm phương án so sánh nếu cài đặt tương thích |

Không nên kết luận mô hình nào luôn tốt hơn trong mọi bài hát. Nếu cần so sánh trong báo cáo, hãy chạy cả hai trên cùng một bộ file và đánh giá theo cùng tiêu chí.

## 3. Cách ứng dụng hoạt động

1. Người dùng chọn file âm thanh trên giao diện Streamlit.
2. Ứng dụng kiểm tra phần mở rộng và giới hạn dung lượng demo.
3. File được ghi tạm vào thư mục tạm của hệ điều hành.
4. Python chạy Demucs bằng `subprocess` với lệnh tương đương:

   ```bash
   python -m demucs --two-stems=vocals -n htdemucs -o <thu_muc_dau_ra> <file_dau_vao>
   ```

5. Demucs xử lý âm thanh và tạo thư mục chứa `vocals.wav`, `no_vocals.wav`.
6. Ứng dụng đọc hai file kết quả vào `st.session_state` để chúng vẫn hiển thị sau khi Streamlit chạy lại giao diện.
7. Người dùng nghe thử và tải hai file WAV.
8. Thư mục tạm được tự động xóa khi khối xử lý kết thúc; dữ liệu âm thanh kết quả cần hiển thị được giữ trong session của ứng dụng.

## 4. Giải thích cấu trúc mã nguồn

### `app.py`

- `import streamlit as st`: sử dụng các thành phần giao diện web của Streamlit.
- `st.set_page_config(...)`: cấu hình tiêu đề, biểu tượng và bố cục trang.
- `st.file_uploader(...)`: tạo nút tải file lên; tham số `type` giới hạn loại file được hiển thị.
- `st.audio(...)`: phát âm thanh ngay trên trang.
- `st.button(...)`: tạo nút bắt đầu quá trình tách.
- `tempfile.TemporaryDirectory(...)`: tạo thư mục tạm và tự dọn thư mục khi thoát khỏi khối `with`.
- `Path.write_bytes(...)`: ghi nội dung file tải lên thành file để Demucs xử lý.
- `subprocess.run(...)`: chạy Demucs như một tiến trình riêng.
- `sys.executable`: bảo đảm dùng Python của môi trường hiện tại, nơi bạn cài các thư viện.
- `--two-stems=vocals`: yêu cầu tách thành vocal và phần không có vocal.
- `-n htdemucs`: chọn mô hình HTDemucs.
- `-o`: chỉ định thư mục đầu ra.
- `capture_output=True`: thu lại thông tin đầu ra và lỗi để hiển thị khi cần.
- `timeout=1800`: giới hạn tiến trình tối đa 30 phút.
- `st.session_state`: lưu kết quả giữa các lần Streamlit chạy lại script.
- `st.download_button(...)`: cho phép tải dữ liệu âm thanh về máy.

### `requirements.txt`

Liệt kê các thư viện Python cần cài:

- `demucs`: thực hiện tách nguồn âm thanh.
- `streamlit`: xây dựng giao diện web.

### `README.md`

Tài liệu hướng dẫn cài đặt, chạy ứng dụng, giải thích kiến trúc và hỗ trợ khắc phục lỗi.

## 5. Streamlit là gì và tại sao dùng?

Streamlit là framework Python giúp tạo ứng dụng web tương tác, đặc biệt phù hợp với demo AI, khoa học dữ liệu và xử lý file.

| Thành phần | Vai trò trong demo |
|---|---|
| `st.title` | Tiêu đề trang |
| `st.write`, `st.caption` | Hiển thị mô tả và hướng dẫn |
| `st.file_uploader` | Chọn file đầu vào |
| `st.audio` | Nghe file đầu vào và kết quả |
| `st.button` | Bắt đầu xử lý |
| `st.spinner` | Hiển thị trạng thái đang chạy |
| `st.error`, `st.success` | Thông báo lỗi hoặc thành công |
| `st.download_button` | Tải file đầu ra |
| `st.session_state` | Giữ kết quả qua các lần cập nhật giao diện |
| `st.columns`, `st.container` | Sắp xếp bố cục giao diện |

**Vì sao chọn Streamlit?**

- Viết giao diện bằng Python, không cần tự xây dựng HTML/CSS/JavaScript.
- Dễ tạo demo để giảng viên hoặc thành viên nhóm trực tiếp thử.
- Có sẵn thành phần tải file, phát âm thanh và tải kết quả.
- Phù hợp cho nguyên mẫu nghiên cứu; không tự động biến ứng dụng thành hệ thống triển khai quy mô lớn.

## 6. Cài đặt trên Windows

### Bước 1 — Giải nén và mở thư mục

Giải nén project, mở thư mục `demucs` bằng VS Code hoặc mở terminal tại thư mục có `app.py`.

### Bước 2 — Kiểm tra Python

```powershell
python --version
```

Nên bắt đầu với Python 3.10 trong môi trường ảo để dễ quản lý thư viện.

### Bước 3 — Tạo và kích hoạt môi trường ảo

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn việc kích hoạt script, có thể mở Command Prompt và chạy:

```bat
.venv\Scripts\activate.bat
```

### Bước 4 — Cài thư viện

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Demucs phụ thuộc PyTorch và một số thư viện âm thanh; quá trình cài đặt có thể mất thời gian.

### Bước 5 — Cài FFmpeg nếu cần

Một số định dạng đầu vào cần FFmpeg. Cài FFmpeg phù hợp với Windows, thêm thư mục `bin` vào `PATH`, sau đó mở terminal mới và kiểm tra:

```powershell
ffmpeg -version
```

Nếu máy báo không nhận lệnh `ffmpeg`, hãy kiểm tra đường dẫn và mở lại terminal.

### Bước 6 — Chạy ứng dụng

```powershell
python -m streamlit run app.py
```

Terminal sẽ hiển thị địa chỉ cục bộ, thường có dạng `http://localhost:8501`. Mở địa chỉ đó trong trình duyệt.

### Bước 7 — Thử demo

1. Chọn một đoạn nhạc có giọng hát.
2. Nghe lại file đầu vào để chắc chắn đã chọn đúng.
3. Nhấn **Tách giọng hát**.
4. Chờ Demucs hoàn thành; lần đầu có thể phải tải mô hình.
5. Nghe phần vocal và instrumental.
6. Tải hai file WAV về máy.

Để dừng ứng dụng, quay lại terminal và nhấn `Ctrl + C`.

## 7. Cách đánh giá kết quả nghiên cứu

Không nên chỉ chứng minh rằng chương trình chạy được. Hãy tạo một bảng thử nghiệm có nhiều kiểu âm thanh:

| Ca kiểm thử | Đặc điểm đầu vào | Điều cần quan sát |
|---|---|---|
| 1 | Giọng hát rõ, nhạc nền đơn giản | Vocal có rõ không? |
| 2 | Giọng hát và nhạc cụ có âm sắc gần nhau | Có bị lọt nhạc vào vocal không? |
| 3 | Giọng hát có vang hoặc hiệu ứng | Phần vang có bị tách sang instrumental không? |
| 4 | Nhiều nhạc cụ, bản phối dày | Vocal còn đầy đủ không? |
| 5 | File rất ngắn hoặc không có giọng hát | Chương trình xử lý và thông báo thế nào? |

Ghi lại cho mỗi thử nghiệm: tên file, thời lượng, thời gian xử lý, chất lượng nghe chủ quan, lỗi phát sinh và nhận xét.

Nếu có bản vocal gốc riêng để đối chiếu, có thể nghiên cứu thêm các chỉ số khách quan như SDR, SI-SDR hoặc các chỉ số đánh giá tách nguồn phù hợp. Nếu không có nguồn tham chiếu, không nên tự đưa ra điểm số khách quan chỉ dựa trên cảm nhận nghe.

## 8. Giới hạn của demo

- Kết quả là ước lượng; không phải bài hát nào cũng tách sạch hoàn toàn.
- File dài có thể cần nhiều RAM, thời gian xử lý và dung lượng lưu trữ.
- GPU có thể tăng tốc nếu môi trường PyTorch và phần cứng được cấu hình tương thích; không nên mặc định máy đang dùng GPU.
- Demo giới hạn file tải lên ở 100 MB, nhưng đây không phải bảo đảm rằng mọi file dưới giới hạn đều xử lý được.
- File đầu ra WAV có thể lớn hơn file MP3 đầu vào.
- Ứng dụng hiện xử lý một file mỗi lần và chưa có hàng đợi tác vụ hoặc lưu lịch sử kết quả lâu dài.

## 9. Lỗi thường gặp

**Lỗi `No module named streamlit` hoặc `No module named demucs`**
- Kiểm tra đã kích hoạt `.venv` chưa.
- Chạy `python -m pip install -r requirements.txt` trong đúng terminal đó.

**Lỗi liên quan FFmpeg hoặc đọc định dạng âm thanh**
- Kiểm tra `ffmpeg -version`.
- Thử một file WAV hoặc MP3 khác để phân biệt lỗi định dạng với lỗi môi trường.

**Lần đầu chạy rất lâu hoặc cần tải model**
- Giữ kết nối mạng trong lần tải mô hình đầu tiên.
- Chờ terminal hoàn tất; không nhấn chạy nhiều lần liên tiếp.

**Máy chậm hoặc hết bộ nhớ**
- Thử một đoạn ngắn hơn.
- Đóng ứng dụng nặng khác.
- Kiểm tra khả năng chạy PyTorch trên GPU nếu máy có GPU tương thích.

**Ứng dụng báo không tìm thấy file đầu ra**
- Xem log trong terminal.
- Kiểm tra Demucs đã chạy thành công và đúng tên mô hình/đường dẫn đầu ra chưa.

## 10. Nội dung cần trình bày khi báo cáo

1. Bài toán: tách vocal khỏi bản nhạc đã trộn.
2. Công nghệ: Demucs, HTDemucs, Python, Streamlit.
3. Sơ đồ xử lý: tải file → Demucs → vocal và instrumental → nghe/tải.
4. Giải thích lệnh Demucs và các phần chính trong `app.py`.
5. Demo trực tiếp với một file âm thanh.
6. Bảng thử nghiệm, nhận xét chất lượng và thời gian xử lý.
7. Hạn chế, lỗi đã gặp và hướng phát triển tiếp theo.

**Hướng phát triển:** bổ sung so sánh Demucs với Spleeter trên cùng bộ dữ liệu; cho phép chọn cấu hình mô hình; hiển thị thời gian xử lý; và kết nối đầu ra vocal với mô-đun phân tích cao độ hoặc đặc trưng giọng hát ở giai đoạn sau.
