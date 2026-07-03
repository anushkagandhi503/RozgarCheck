import streamlit as st
import re
from bias_words import MASCULINE_CODED, FEMININE_CODED, CULTURAL_BIAS, SUGGESTIONS
from detector import analyze_job_description, get_model

st.set_page_config(
    page_title="RozgarCheck — JD Bias Detector",
    page_icon="🔍",
    layout="centered"
)

st.markdown("""
<style>
    .bias-box {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #7c6af7;
        color: white;
    }
    .word-masc { background:#3d2b5e; color:#c9b8ff; padding:2px 8px; border-radius:4px; margin:2px; display:inline-block; }
    .word-fem  { background:#1e3a4a; color:#7ee8d8; padding:2px 8px; border-radius:4px; margin:2px; display:inline-block; }
    .word-cult { background:#4a2a1e; color:#f7b26a; padding:2px 8px; border-radius:4px; margin:2px; display:inline-block; }
    .flag-box {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        border-left: 4px solid #f7b26a;
        color: white;
        font-size: 0.95em;
    }
    .flag-sentence { color: #ff9999; font-weight: bold; margin-bottom: 6px; }
    .flag-reason   { color: #cccccc; margin-bottom: 4px; }
    .flag-fix      { color: #7ee8d8; }
    .method-rule   { background:#3d2b5e; color:#c9b8ff; padding:1px 7px; border-radius:4px; font-size:0.8em; }
    .method-sem    { background:#1e3a4a; color:#7ee8d8; padding:1px 7px; border-radius:4px; font-size:0.8em; }
</style>
""", unsafe_allow_html=True)


# ── Load semantic model once at startup ──────────────────────────────────────
@st.cache_resource
def load_model():
    return get_model()

load_model()


# ── Original detection logic (unchanged) ────────────────────────────────────
def analyze_jd(text):
    text_lower = text.lower()
    found_masc, found_fem, found_cult = [], [], []

    for word in MASCULINE_CODED:
        if word in text_lower:
            found_masc.append(word)
    for word in FEMININE_CODED:
        if word in text_lower:
            found_fem.append(word)
    for phrase in CULTURAL_BIAS:
        if phrase in text_lower:
            found_cult.append(phrase)

    total = len(found_masc) + len(found_fem) + len(found_cult)

    if total == 0:      score = 100
    elif total <= 2:    score = 80
    elif total <= 5:    score = 55
    elif total <= 9:    score = 30
    else:               score = 10

    return {"masculine": found_masc, "feminine": found_fem,
            "cultural": found_cult, "score": score, "total": total}


def clean_jd(text, results):
    cleaned = text
    for word in results["masculine"] + results["feminine"] + results["cultural"]:
        replacement = SUGGESTIONS.get(word, f"[neutral alternative for '{word}']")
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        cleaned = pattern.sub(f"**{replacement}**", cleaned)
    return cleaned


# ── UI ───────────────────────────────────────────────────────────────────────
st.title("🔍 RozgarCheck")
st.markdown("**Detect gender and cultural bias in job descriptions — instantly.**")
st.markdown("---")

sample_jd = """We are looking for a competitive and aggressive rockstar developer
who can dominate in a fast-paced environment. The ideal candidate is a self-reliant
individual contributor with excellent English and neutral accent.
Only candidates from tier 1 colleges need apply.
You must be driven, fearless, and ready to crush targets every quarter."""

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("##### Paste a Job Description below")
with col2:
    if st.button("Load Sample JD"):
        st.session_state["jd_text"] = sample_jd

jd_input = st.text_area(
    label="Job Description",
    value=st.session_state.get("jd_text", ""),
    height=220,
    placeholder="Paste the job description here...",
    label_visibility="collapsed"
)

if st.button("🔍 Analyse for Bias", use_container_width=True, type="primary"):
    if not jd_input.strip():
        st.warning("Please paste a job description first.")
    else:
        # ── Layer 1: Original word-level analysis (unchanged) ────────────────
        results = analyze_jd(jd_input)
        score = results["score"]

        st.markdown("---")
        st.markdown("## 📊 Results")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Bias-Free Score", f"{score}/100")
        with c2:
            st.metric("Bias Words Found", results["total"])
        with c3:
            verdict = "✅ Clean" if score >= 75 else ("⚠️ Review" if score >= 40 else "🚨 Biased")
            st.metric("Verdict", verdict)

        if score >= 75:
            st.success("✅ This JD looks fairly neutral. Minor improvements possible.")
        elif score >= 40:
            st.warning("⚠️ Moderate bias detected. Some candidates may be discouraged from applying.")
        else:
            st.error("🚨 High bias detected. This JD likely filters out qualified diverse candidates.")

        if results["masculine"]:
            st.markdown("### 💜 Masculine-Coded Words")
            st.markdown("These words statistically attract more male applicants and discourage women.")
            st.markdown(" ".join([f'<span class="word-masc">{w}</span>' for w in results["masculine"]]), unsafe_allow_html=True)

        if results["feminine"]:
            st.markdown("### 🩵 Feminine-Coded Words")
            st.markdown("These words may signal a culture that deters some applicants.")
            st.markdown(" ".join([f'<span class="word-fem">{w}</span>' for w in results["feminine"]]), unsafe_allow_html=True)

        if results["cultural"]:
            st.markdown("### 🟠 Cultural / Credential Bias")
            st.markdown("These phrases may exclude candidates based on background or accent.")
            st.markdown(" ".join([f'<span class="word-cult">{w}</span>' for w in results["cultural"]]), unsafe_allow_html=True)

        if results["total"] == 0:
            st.balloons()
            st.success("🎉 Zero bias words detected! This is an excellent, inclusive job description.")

        st.markdown("---")
        st.markdown("## ✍️ Suggested Clean Version")
        cleaned = clean_jd(jd_input, results)
        st.markdown(f'<div class="bias-box">{cleaned}</div>', unsafe_allow_html=True)

        st.download_button(
            label="⬇️ Download Clean JD",
            data=cleaned,
            file_name="clean_jd.txt",
            mime="text/plain"
        )

        # ── Layer 2: Semantic deep analysis (new) ────────────────────────────
        st.markdown("---")
        st.markdown("## 🧠 Deep Semantic Analysis")
        st.markdown("Catches paraphrased and context-dependent bias that word lists miss — powered by sentence embeddings.")

        with st.spinner("Running semantic analysis..."):
            semantic_results = analyze_job_description(jd_input)

        sem_flags = semantic_results["flags"]

        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("Sentences Scanned", semantic_results["total_sentences"])
        with s2:
            st.metric("Semantic Flags", semantic_results["total_flags"])
        with s3:
            cats = len(semantic_results["categories_triggered"])
            st.metric("Categories Triggered", cats)

        if sem_flags:
            for i, flag in enumerate(sem_flags, 1):
                method_badge = '<span class="method-rule">🔵 Rule</span>' if flag["method"] == "rule" else '<span class="method-sem">🟣 Semantic</span>'
                confidence_pct = int(flag["confidence"] * 100)
                st.markdown(
                    f'<div class="flag-box">'
                    f'<div style="margin-bottom:6px">{method_badge} &nbsp;<strong>{flag["category_label"]}</strong> &nbsp;'
                    f'<span style="color:#888;font-size:0.85em">confidence: {confidence_pct}%</span></div>'
                    f'<div class="flag-sentence">"{flag["sentence"]}"</div>'
                    f'<div class="flag-reason">⚠️ {flag["reason"]}</div>'
                    f'<div class="flag-fix">✏️ {flag["suggested_rewrite"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.success("✅ No semantic bias patterns detected beyond the word-level analysis above.")

        st.markdown(
            "<small>🔒 Audit log entry created. Input hashed, not stored in raw form.</small>",
            unsafe_allow_html=True
        )

st.markdown("---")
st.markdown("<small>Built by Anushka Gandhi · MMCOE + IIT Madras · Powered by Python & Streamlit</small>", unsafe_allow_html=True)
