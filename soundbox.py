"""Soundbox simulation component.
Produces formatted visual soundbox displays, audio generation,
and safe execution guards for verified transactions.
Supports English and Hindi audio announcements and high-tech realistic device rendering.
"""

import os
import base64
import html
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from config import (
    AUDIO_DIR,
    SOUNDBOX_TEXT_TEMPLATE_EN,
    SOUNDBOX_FULL_SPEECH_EN,
    SOUNDBOX_TEXT_TEMPLATE_HI,
    SOUNDBOX_FULL_SPEECH_HI,
    CURRENCY_SYMBOL
)

# Optional gTTS import with graceful fallback
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Optional pyttsx3 import with graceful fallback
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

def format_announcement_text(amount: float, lang: str = "en") -> str:
    """Format the standard concise soundbox announcement message in EN or HI."""
    formatted_amount = f"{amount:g}" if amount.is_integer() else f"{amount:,.2f}"
    if lang == "hi":
        return SOUNDBOX_TEXT_TEMPLATE_HI.format(amount=formatted_amount)
    return SOUNDBOX_TEXT_TEMPLATE_EN.format(amount=formatted_amount)

def format_full_speech_sentence(amount: float, lang: str = "en") -> str:
    """Format the full speech sentence spoken by the simulated soundbox in EN or HI."""
    formatted_amount = f"{amount:g}" if amount.is_integer() else f"{amount:,.2f}"
    if lang == "hi":
        return SOUNDBOX_FULL_SPEECH_HI.format(amount=formatted_amount)
    return SOUNDBOX_FULL_SPEECH_EN.format(amount=formatted_amount)

def generate_speech_audio_file(
    amount: float, 
    tx_id: str, 
    lang: str = "en"
) -> Tuple[Optional[str], Optional[bytes], str]:
    """Generate an audio file for the payment announcement.
    
    Returns:
        (file_path_or_none, audio_bytes_or_none, engine_used_description)
    """
    sentence = format_full_speech_sentence(amount, lang=lang)
    clean_tx = tx_id.replace(" ", "_").replace(":", "-")
    output_filename = f"soundbox_{clean_tx}_{int(amount)}_{lang}.mp3"
    output_path = AUDIO_DIR / output_filename

    # If already cached, reuse
    if output_path.exists():
        try:
            with open(output_path, "rb") as f:
                data = f.read()
            return str(output_path), data, f"Cached Audio ({lang.upper()})"
        except Exception:
            pass

    # Try gTTS first
    if GTTS_AVAILABLE:
        try:
            tts_lang = "hi" if lang == "hi" else "en"
            tld = "co.in" if lang == "en" else "com"
            tts = gTTS(text=sentence, lang=tts_lang, tld=tld, slow=False)
            tts.save(str(output_path))
            with open(output_path, "rb") as f:
                data = f.read()
            return str(output_path), data, f"Google TTS ({lang.upper()} Engine)"
        except Exception:
            # Fall through if offline or rate-limited
            pass

    # Try pyttsx3 offline next
    if PYTTSX3_AVAILABLE:
        try:
            wav_output = AUDIO_DIR / f"soundbox_{clean_tx}_{int(amount)}_{lang}.wav"
            engine = pyttsx3.init()
            engine.setProperty("rate", 145)
            engine.save_to_file(sentence, str(wav_output))
            engine.runAndWait()
            if wav_output.exists():
                with open(wav_output, "rb") as f:
                    data = f.read()
                return str(wav_output), data, "pyttsx3 (Offline SAPI)"
        except Exception:
            pass

    # Graceful fallback: audio generated client-side via Web Speech API
    return None, None, f"Browser Web Speech API ({lang.upper()})"

def render_soundbox_html(
    amount: float,
    tx_id: str,
    status: str = "VERIFIED",
    audio_base64: Optional[str] = None,
    audio_format: str = "audio/mp3",
    lang: str = "en"
) -> str:
    """Generate state-of-the-art, hyper-realistic FinTech IoT Soundbox HTML/CSS component."""
    announcement_en = format_announcement_text(amount, "en")
    speech_en = format_full_speech_sentence(amount, "en")
    announcement_hi = format_announcement_text(amount, "hi")
    speech_hi = format_full_speech_sentence(amount, "hi")

    primary_announcement = announcement_hi if lang == "hi" else announcement_en
    formatted_amount = f"{amount:g}" if amount.is_integer() else f"{amount:,.2f}"

    is_verified = (status.upper() in ("VERIFIED", "CONFIRMED"))
    is_standby = (status.upper() == "STANDBY")

    if is_verified:
        led_color = "#10b981"  # Emerald
        led_glow = "rgba(16, 185, 129, 0.6)"
        status_label = "VERIFIED & CONFIRMED"
        status_bg = "rgba(16, 185, 129, 0.15)"
        status_border = "#10b981"
        speaker_icon = "🔊"
        box_glow = "0 20px 50px rgba(16, 185, 129, 0.25), 0 0 0 1px rgba(16, 185, 129, 0.3)"
    elif is_standby:
        led_color = "#38bdf8"  # Sky Blue
        led_glow = "rgba(56, 189, 248, 0.5)"
        status_label = "READY FOR PAYMENT"
        status_bg = "rgba(56, 189, 248, 0.15)"
        status_border = "#38bdf8"
        speaker_icon = "📶"
        box_glow = "0 20px 45px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(56, 189, 248, 0.2)"
    else:
        led_color = "#ef4444"  # Rose Red
        led_glow = "rgba(239, 68, 68, 0.6)"
        status_label = "MUTATION / TAMPER ALERT"
        status_bg = "rgba(239, 68, 68, 0.15)"
        status_border = "#ef4444"
        speaker_icon = "🔇"
        box_glow = "0 20px 50px rgba(239, 68, 68, 0.3), 0 0 0 1px rgba(239, 68, 68, 0.4)"

    audio_tag = ""
    if audio_base64:
        audio_tag = f"""
        <audio autoplay controls style="width: 100%; height: 32px; margin-top: 12px; border-radius: 8px; filter: invert(0.85) hue-rotate(180deg);">
            <source src="data:{audio_format};base64,{audio_base64}" type="{audio_format}">
        </audio>
        """

    safe_en = html.escape(speech_en)
    safe_hi = html.escape(speech_hi)

    # Equalizer wave animation bars
    eq_bars = "".join([
        f'<div class="sb-eq-bar" style="animation-delay: {i * 0.12}s;"></div>'
        for i in range(12)
    ]) if is_verified else ""

    html_code = f"""
    <div class="soundbox-device-wrapper">
        <style>
            @keyframes sbPulse {{
                0% {{ box-shadow: 0 0 0 0 {led_glow}; }}
                70% {{ box-shadow: 0 0 0 10px rgba(0,0,0,0); }}
                100% {{ box-shadow: 0 0 0 0 rgba(0,0,0,0); }}
            }}
            @keyframes sbWave {{
                0%, 100% {{ height: 4px; }}
                50% {{ height: 26px; }}
            }}
            .soundbox-device-wrapper {{
                background: linear-gradient(165deg, #131c2e 0%, #0a0f1d 60%, #070a14 100%);
                border-radius: 28px;
                padding: 24px;
                color: #ffffff;
                box-shadow: {box_glow};
                max-width: 520px;
                margin: 12px auto;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }}
            .soundbox-device-wrapper::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, transparent, {led_color}, transparent);
            }}
            .sb-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 18px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                padding-bottom: 12px;
            }}
            .sb-led-group {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .sb-led {{
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background-color: {led_color};
                box-shadow: 0 0 12px {led_color};
                animation: sbPulse 1.8s infinite;
            }}
            .sb-brand {{
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 2px;
                color: #e2e8f0;
                text-transform: uppercase;
            }}
            .sb-status-badge {{
                background: {status_bg};
                color: {led_color};
                font-size: 11px;
                font-weight: 700;
                padding: 4px 12px;
                border-radius: 20px;
                border: 1px solid {status_border};
                letter-spacing: 0.6px;
                text-transform: uppercase;
            }}
            .sb-speaker-grill {{
                background: radial-gradient(circle, #0e172a 0%, #060913 100%);
                border-radius: 18px;
                padding: 20px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.06);
                box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.6);
                margin-bottom: 16px;
                position: relative;
            }}
            .sb-equalizer {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 4px;
                height: 30px;
                margin-bottom: 10px;
            }}
            .sb-eq-bar {{
                width: 4px;
                background: linear-gradient(to top, #00f2fe, #4facfe, #10b981);
                border-radius: 4px;
                animation: sbWave 0.9s ease-in-out infinite;
            }}
            .sb-oled-screen {{
                background: #020617;
                border-radius: 14px;
                padding: 14px 18px;
                border: 1px solid rgba(56, 189, 248, 0.25);
                box-shadow: inset 0 0 16px rgba(0, 242, 254, 0.1);
                margin-bottom: 14px;
            }}
            .sb-lcd-sub {{
                color: #94a3b8;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                margin-bottom: 4px;
                display: flex;
                justify-content: space-between;
            }}
            .sb-amount-val {{
                font-size: 34px;
                font-weight: 900;
                color: #ffffff;
                letter-spacing: -1px;
                text-shadow: 0 0 12px rgba(255, 255, 255, 0.2);
            }}
            .sb-voice-text {{
                font-size: 16px;
                font-weight: 700;
                color: #38bdf8;
                margin-top: 6px;
                line-height: 1.4;
            }}
            .sb-actions {{
                display: flex;
                gap: 8px;
                justify-content: center;
                margin-top: 14px;
                flex-wrap: wrap;
            }}
            .sb-play-btn {{
                background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(16, 185, 129, 0.2));
                color: #e2e8f0;
                border: 1px solid rgba(56, 189, 248, 0.4);
                padding: 7px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}
            .sb-play-btn:hover {{
                background: linear-gradient(135deg, #00f2fe, #4facfe);
                color: #020617;
                border-color: #00f2fe;
                box-shadow: 0 4px 14px rgba(0, 242, 254, 0.4);
                transform: translateY(-1px);
            }}
        </style>

        <!-- Hardware Header -->
        <div class="sb-header">
            <div class="sb-led-group">
                <div class="sb-led"></div>
                <div class="sb-brand">SECURE SOUNDBOX IoT</div>
            </div>
            <div class="sb-status-badge">{status_label}</div>
        </div>

        <!-- Speaker Acoustic Grill -->
        <div class="sb-speaker-grill">
            <div class="sb-equalizer">
                {eq_bars}
            </div>
            <div style="font-size: 36px; margin: 2px 0;">{speaker_icon}</div>
            <div class="sb-voice-text">"{primary_announcement}"</div>
        </div>

        <!-- Digital OLED Screen -->
        <div class="sb-oled-screen">
            <div class="sb-lcd-sub">
                <span>SIMULATED SETTLEMENT</span>
                <span style="color: {led_color};">● LIVE SPEAKER</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: baseline;">
                <div class="sb-amount-val">{CURRENCY_SYMBOL}{formatted_amount}</div>
                <div style="font-size: 12px; color: #94a3b8; font-family: monospace;">SHA-256 SIGNED</div>
            </div>
        </div>

        <!-- Footnote Info -->
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b; font-family: monospace; padding: 0 4px;">
            <span>TX: <span style="color: #38bdf8;">{tx_id}</span></span>
            <span>Status: <b style="color: {led_color};">{status}</b></span>
        </div>

        <!-- Optional Python Audio Player -->
        {audio_tag}

        <!-- Interactive Browser Speech Trigger Controls -->
        <div class="sb-actions">
            <button 
                class="sb-play-btn"
                onclick="
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const utt = new SpeechSynthesisUtterance('{safe_en}');
                        utt.rate = 1.0;
                        utt.pitch = 1.0;
                        utt.lang = 'en-IN';
                        window.speechSynthesis.speak(utt);
                    }} else {{
                        alert('Browser Speech Synthesis not supported.');
                    }}
                "
            >
                <span>🔊</span> Play English
            </button>
            <button 
                class="sb-play-btn"
                onclick="
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const utt = new SpeechSynthesisUtterance('{safe_hi}');
                        utt.rate = 0.95;
                        utt.pitch = 1.0;
                        utt.lang = 'hi-IN';
                        window.speechSynthesis.speak(utt);
                    }} else {{
                        alert('Browser Speech Synthesis not supported.');
                    }}
                "
            >
                <span>🇮🇳</span> हिन्दी में सुनें
            </button>
        </div>
    </div>
    """
    return html_code

def trigger_verified_soundbox_announcement(
    record: Dict[str, Any],
    is_verified: bool,
    lang: str = "en"
) -> Dict[str, Any]:
    """Announce payment ONLY when cryptographic verification check passes.
    
    Guards:
    - If is_verified is False, refuses to announce success and raises/returns rejection.
    """
    if not is_verified:
        return {
            "success": False,
            "message": "Security Guard Triggered: Unverified or tampered payment cannot be announced.",
            "announcement_text": "Payment validation failed. Announcement blocked.",
            "audio_file": None,
            "audio_bytes": None,
            "engine_info": "Blocked by Security Guard",
            "html": render_soundbox_html(
                amount=float(record.get("amount", 0)),
                tx_id=str(record.get("tx_id", "UNKNOWN")),
                status="FAILED",
                lang=lang
            )
        }

    amount = float(record["amount"])
    tx_id = str(record["tx_id"])
    announcement_text = format_announcement_text(amount, lang=lang)

    audio_file, audio_bytes, engine_info = generate_speech_audio_file(amount, tx_id, lang=lang)
    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None

    html_code = render_soundbox_html(
        amount=amount,
        tx_id=tx_id,
        status="VERIFIED",
        audio_base64=audio_base64,
        lang=lang
    )

    return {
        "success": True,
        "message": "Payment verified and soundbox announced successfully.",
        "announcement_text": announcement_text,
        "audio_file": audio_file,
        "audio_bytes": audio_bytes,
        "engine_info": engine_info,
        "html": html_code
    }
