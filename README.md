# Demo tách giọng hát

Ứng dụng Streamlit dùng Demucs (mô hình HTDemucs) để tách một file có giọng hát
và nhạc nền thành hai file WAV: `vocals.wav` và `instrumental.wav`.

## Yêu cầu

- Python 3.10–3.12
- FFmpeg được cài đặt và có trong `PATH` để đọc các định dạng âm thanh phổ biến
- PyTorch chạy được trên máy; lần đầu chạy có thể tải mô hình HTDemucs

## Chạy ứng dụng

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Mở địa chỉ Streamlit hiển thị trong terminal, tải lên một file MP3, WAV, FLAC,
OGG hoặc M4A rồi chọn **Tách giọng hát**. Kết quả có thể nghe trực tiếp hoặc
tải về. Mặc định Demucs xử lý trên CPU; thời gian chạy phụ thuộc vào độ dài
đoạn nhạc và cấu hình máy.

## Thông tin demo

- **Đầu vào:** một đoạn hát có nhạc
- **Đầu ra:** vocal và instrumental
- **Người thực hiện:** Nguyễn Bá Thành
- **Thời gian:** 22/09/2026–10/10/2026
