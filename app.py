from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st


# -------------------- Cấu hình ứng dụng --------------------
APP_TITLE = "Tách giọng hát"
SUPPORTED_TYPES = ["mp3", "wav", "flac", "ogg", "m4a"]
MAX_FILE_SIZE_MB = 100
MODEL_NAME = "htdemucs"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Tách giọng hát khỏi nhạc nền")
st.write(
    "Tải lên một đoạn nhạc có giọng hát. Ứng dụng dùng Demucs để tạo "
    "hai bản âm thanh: vocal (giọng hát) và instrumental (nhạc nền)."
)

with st.expander("Thông tin đề tài", expanded=False):
    st.write("**Công nghệ:** Python, Streamlit, Demucs / HTDemucs")
    st.write("**Người thực hiện:** Nguyễn Bá Thành")
    st.write("**Thời gian:** 22/09/2026 – 10/10/2026")
    st.write(
        "**Mục tiêu:** xây dựng demo có thể tải file âm thanh lên, "
        "tách giọng hát, nghe thử và tải hai kết quả về máy."
    )

st.info(
    "Lưu ý: lần chạy đầu tiên Demucs có thể cần tải mô hình. "
    "Thời gian xử lý phụ thuộc độ dài âm thanh, CPU/GPU và cấu hình máy."
)

uploaded_file = st.file_uploader(
    "1. Chọn file âm thanh",
    type=SUPPORTED_TYPES,
    help="Hỗ trợ MP3, WAV, FLAC, OGG và M4A.",
    key="audio_upload",
)

# Nếu người dùng đổi file, không hiển thị nhầm kết quả của file trước.
current_signature = (
    uploaded_file.name,
    uploaded_file.size,
) if uploaded_file is not None else None

if st.session_state.get("input_signature") != current_signature:
    st.session_state.pop("separated_audio", None)
    st.session_state["input_signature"] = current_signature

if uploaded_file is not None:
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"File vượt quá giới hạn demo {MAX_FILE_SIZE_MB} MB. Hãy chọn file nhỏ hơn.")
        can_process = False
    else:
        st.caption(
            f"Đã chọn: {uploaded_file.name} · "
            f"{uploaded_file.size / (1024 * 1024):.2f} MB"
        )
        st.audio(uploaded_file)
        can_process = True
else:
    st.caption("Chưa có file âm thanh.")
    can_process = False

if st.button(
    "2. Tách giọng hát",
    type="primary",
    disabled=not can_process,
    use_container_width=True,
):
    st.session_state.pop("separated_audio", None)

    with st.spinner("Demucs đang xử lý. Vui lòng chờ..."):
        try:
            # TemporaryDirectory tự dọn file đầu vào và file trung gian
            # sau khi đã đọc hai file kết quả vào session_state.
            with tempfile.TemporaryDirectory(prefix="vocal-separation-") as temp:
                work_dir = Path(temp)
                suffix = Path(uploaded_file.name).suffix.lower()
                input_path = work_dir / f"input_audio{suffix}"
                output_dir = work_dir / "separated"
                input_path.write_bytes(uploaded_file.getvalue())

                command = [
                    sys.executable,
                    "-m",
                    "demucs",
                    "--two-stems=vocals",
                    "-n",
                    MODEL_NAME,
                    "-o",
                    str(output_dir),
                    str(input_path),
                ]

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=1800,  # Giới hạn 30 phút cho demo
                    check=False,
                )

                if result.returncode != 0:
                    details = (result.stderr or result.stdout).strip()
                    if not details:
                        details = f"Demucs kết thúc với mã lỗi {result.returncode}."
                    st.error("Tách âm thanh thất bại. Chi tiết lỗi:")
                    st.code(details[-4000:])
                else:
                    # Với --two-stems=vocals, Demucs tạo vocals.wav và no_vocals.wav.
                    stem_dir = output_dir / MODEL_NAME / input_path.stem
                    vocals_path = stem_dir / "vocals.wav"
                    instrumental_path = stem_dir / "no_vocals.wav"

                    if not vocals_path.is_file() or not instrumental_path.is_file():
                        st.error(
                            "Demucs đã chạy nhưng không tìm thấy đủ hai file đầu ra. "
                            "Kiểm tra log trong terminal để biết thêm chi tiết."
                        )
                    else:
                        st.session_state["separated_audio"] = {
                            "vocals": vocals_path.read_bytes(),
                            "instrumental": instrumental_path.read_bytes(),
                            "name": Path(uploaded_file.name).stem,
                        }

        except subprocess.TimeoutExpired:
            st.error("Quá trình tách vượt quá 30 phút và đã bị dừng.")
        except OSError as exc:
            st.error(f"Không thể chạy Demucs hoặc đọc/ghi file: {exc}")

separated_audio = st.session_state.get("separated_audio")

if separated_audio:
    st.success("Tách âm thanh hoàn tất!")
    st.subheader("3. Nghe và tải kết quả")

    with st.container(border=True):
        st.markdown("**Vocal — giọng hát**")
        st.caption("Bản âm thanh tập trung vào giọng hát; có thể còn sót một phần nhạc nền.")
        st.audio(separated_audio["vocals"], format="audio/wav")
        st.download_button(
            "Tải vocal.wav",
            data=separated_audio["vocals"],
            file_name=f"{separated_audio['name']}_vocals.wav",
            mime="audio/wav",
            key="download_vocals",
            use_container_width=True,
        )

    with st.container(border=True):
        st.markdown("**Instrumental — nhạc nền**")
        st.caption("Phần âm thanh còn lại sau khi ước lượng và tách vocal.")
        st.audio(separated_audio["instrumental"], format="audio/wav")
        st.download_button(
            "Tải instrumental.wav",
            data=separated_audio["instrumental"],
            file_name=f"{separated_audio['name']}_instrumental.wav",
            mime="audio/wav",
            key="download_instrumental",
            use_container_width=True,
        )

st.divider()
st.caption(
    "Kết quả tách bằng AI là kết quả ước lượng, không đảm bảo sạch hoàn toàn. "
    "Chất lượng phụ thuộc bản phối, hiệu ứng, tiếng vang và chất lượng file đầu vào."
)
