import streamlit as st

# Sin líneas en blanco dentro del <style>: markdown cortaría el bloque.
_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
:root{--ember:#ff4700;--ember-glow:#8b2e09;--ember-smoke:#451e0e;--obsidian:#0f0d0a;--graphite:#161412;--ash:#cccccc;--bone:#ffffff;--line:rgba(204,204,204,.22);--font:'Helvetica Neue',Inter,ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;}
.stApp,.stApp button,.stApp input,.stApp textarea,.stApp [data-baseweb]{font-family:var(--font);}
[data-testid="stIconMaterial"],.material-icons{font-family:'Material Symbols Rounded' !important;}
.stApp p,.stApp label,.stApp li{font-size:15px;line-height:1.5;}
.stApp [data-testid="stCaptionContainer"]{color:var(--ash);font-size:13px;letter-spacing:.01em;}
header[data-testid="stHeader"]{background:transparent;}
#MainMenu,footer{visibility:hidden;}
.block-container{padding-top:2.5rem;padding-bottom:5rem;}
.stApp h1{font-size:40px;font-weight:700;line-height:1;letter-spacing:-.021em;padding:0 0 .5rem;}
.stApp h2,.stApp h3{font-size:22px;font-weight:500;line-height:1.2;letter-spacing:0;}
.hero{text-align:center;padding:24px 0 32px;}
.hero .display{font-size:clamp(64px,22vw,140px);font-weight:700;line-height:.9;letter-spacing:-.021em;color:var(--bone);margin:24px 0 16px;}
.hero .sub{color:var(--ash);font-size:15px;line-height:1.5;margin:0;}
.chip{display:inline-block;background:var(--graphite);border:1px solid var(--ash);border-radius:9999px;padding:4px 14px;color:var(--ash);font-size:13px;letter-spacing:.01em;}
.muted{color:var(--ash);font-size:13px;letter-spacing:.01em;}
.habit{padding-bottom:6px;display:flex;justify-content:space-between;align-items:center;gap:16px;}
.streak{text-align:right;font-size:22px;font-weight:700;line-height:1;letter-spacing:-.021em;white-space:nowrap;}
.streak small{display:block;color:var(--ash);font-size:13px;font-weight:400;letter-spacing:.01em;margin-top:4px;}
.stApp [data-testid="stHorizontalBlock"]{flex-wrap:nowrap !important;gap:12px;}
.stApp [data-testid="stColumn"]{min-width:0 !important;width:auto !important;flex:1 1 0 !important;}
.mark{display:inline-block;width:1.1em;font-size:15px;}
.mark.on{color:var(--ember);}
.mark.off,.mark.none{color:var(--ash);}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stForm"]{border-radius:0 !important;border-color:var(--line) !important;}
[data-testid="stMetricLabel"]{color:var(--ash);font-size:13px;letter-spacing:.01em;}
[data-testid="stMetricValue"]{font-weight:700;letter-spacing:-.021em;}
[data-testid^="stBaseButton-primary"]{background:var(--ember);color:var(--bone);border:none;border-radius:4px;font-weight:500;padding:12px 16px;box-shadow:0 0 0 1px var(--ember-smoke),0 0 24px 4px var(--ember-glow);}
[data-testid^="stBaseButton-primary"]:hover{background:var(--ember);filter:brightness(1.1);}
[data-testid^="stBaseButton-secondary"]{background:transparent;color:var(--ash);border:1px solid var(--line);border-radius:4px;}
[data-testid="stPageLink-NavLink"]{border-radius:9999px;}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{border-radius:4px !important;}
[data-testid="stAlert"]{background:var(--graphite);border:1px solid var(--line);border-radius:0;color:var(--ash);}
</style>"""


def setup(page_title: str) -> None:
    """Debe ser lo primero que llama cada página."""
    st.set_page_config(page_title=page_title, layout="centered")
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(chip: str, title: str, subtitle: str) -> None:
    """Cabecera centrada: chip, titular grande y una línea de apoyo."""
    st.markdown(
        f'<div class="hero"><span class="chip">{chip}</span>'
        f'<div class="display">{title}</div>'
        f'<p class="sub">{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def mark(met) -> str:
    """Marca de estado: ● cumplido, ○ no cumplido, · sin dato (la forma, no solo el color)."""
    if met is None:
        return '<span class="mark none">·</span>'
    return '<span class="mark on">●</span>' if met else '<span class="mark off">○</span>'
