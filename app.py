from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st


APP_TITLE = "Tách giọng hát"
SUPPORTED_TYPES = ["mp3", "wav", "flac", "ogg", "m4a"]

st.set_page_config(page_title=APP_TITLE, page_icon="🎙️", layout="centered")

st.title("🎙️ Tách giọng hát")
st.caption("Demo tách vocal và nhạc nền bằng Demucs (HTDemucs)")

with st.container(border=True):
    st.subheader("Thông tin demo")
    col1, col2 = st.columns(2)
    col1.metric("Trạng thái", "Đang thực hiện")
    col2.metric("Công nghệ", "Demucs / HTDemucs")
    st.write("**Người thực hiện:** Nguyễn Bá Thành")
    st.write("**Thời gian:** 22/09/2026 – 10/10/2026")

st.markdown(
    "Tải lên **một đoạn hát có nhạc**. Demo sẽ tạo hai bản âm thanh: "
    "**Vocal** (giọng hát) và **Instrumental** (nhạc nền, không có giọng hát)."
)

uploaded_file = st.file_uploader(
    "Chọn file âm thanh",
    type=SUPPORTED_TYPES,
    help="Hỗ trợ MP3, WAV, FLAC, OGG và M4A.",
)

if uploaded_file is not None:
    st.audio(uploaded_file)

if st.button(
    "Tách giọng hát",
    type="primary",
    disabled=uploaded_file is None,
    use_container_width=True,
):
    if uploaded_file is None:
        st.warning("Vui lòng chọn file âm thanh trước.")
    else:
        st.session_state.pop("separated_audio", None)
        with st.spinner("Demucs đang tách âm thanh. Quá trình có thể mất vài phút..."):
            try:
                with tempfile.TemporaryDirectory(prefix="vocal-separation-") as temp:
                    work_dir = Path(temp)
                    input_path = work_dir / f"audio{Path(uploaded_file.name).suffix.lower()}"
                    output_dir = work_dir / "separated"
                    input_path.write_bytes(uploaded_file.getvalue())

                    result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "demucs",
                            "--two-stems=vocals",
                            "-n",
                            "htdemucs",
                            "-o",
                            str(output_dir),
                            str(input_path),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=1800,
                        check=False,
                    )

                    if result.returncode != 0:
                        details = (result.stderr or result.stdout).strip()
                        if not details:
                            details = f"Demucs kết thúc với mã lỗi {result.returncode}."
                        st.error(f"Tách âm thanh thất bại:\n\n{details[-3000:]}")
                    else:
                        stem_dir = output_dir / "htdemucs" / input_path.stem
                        vocals_path = stem_dir / "vocals.wav"
                        instrumental_path = stem_dir / "no_vocals.wav"

                        if not vocals_path.is_file() or not instrumental_path.is_file():
                            st.error(
                                "Demucs chạy xong nhưng không tìm thấy đủ hai file "
                                "đầu ra mong đợi."
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
                st.error(f"Không thể chạy Demucs hoặc đọc file âm thanh: {exc}")

separated_audio = st.session_state.get("separated_audio")
if separated_audio:
    st.subheader("Kết quả tách")
    for key, label, filename in (
        ("vocals", "Vocal – giọng hát", "vocals.wav"),
        ("instrumental", "Instrumental – nhạc nền", "instrumental.wav"),
    ):
        st.markdown(f"**{label}**")
        st.audio(separated_audio[key], format="audio/wav")
        st.download_button(
            f"Tải {filename}",
            data=separated_audio[key],
            file_name=f"{separated_audio['name']}_{filename}",
            mime="audio/wav",
            key=f"download_{key}",
            use_container_width=True,
        )
