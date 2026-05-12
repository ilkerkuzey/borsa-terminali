import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SAYFA VE MOBİL OPTİMİZE CSS ---
st.set_page_config(page_title="AI Teknik Analiz", layout="wide")

st.markdown("""
    <style>
    * 1. Menüye tıklandığında aşağı açılan listenin (popover) arka planını karart */
    div[data-baseweb="popover"], 
    div[data-baseweb="popover"] *, 
    ul[role="listbox"], 
    li[role="option"] {
        background-color: #0d1a17 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* 2. Liste üzerindeki seçili (hover) elemanın rengini belirle */
    li[role="option"]:hover {
        background-color: #162a26 !important;
    }

    /* 3. Menü kutusunun içindeki yazıyı mobilde tekrar garantiye al */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #162a26 !important;
        color: white !important;
    }
    /* Genel Arka Plan */
    .stApp { background-color: #0b1e1a !important; }
    [data-testid="stSidebar"] { background-color: #0d1a17 !important; }

    /* MOBİLDEKİ SOLUK YAZI SORUNUNU KÖKTEN ÇÖZEN AYAR */
    input, select, textarea, [data-baseweb="select"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }
    
    /* Input Kutularının Arka Planı */
    [data-baseweb="base-input"], [data-baseweb="select"] {
        background-color: #162a26 !important;
        border-radius: 8px !important;
    }

    /* Yazı Renklerini Parlat */
    h1, h2, h3, p, span, div, label { color: #ffffff !important; }
    
    /* Üst Çubuk ve İkon Ayarı */
    header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; height: 3.5rem !important; }
    button[kind="header"] { color: #ffffff !important; }
    .block-container { padding-top: 3rem !important; padding-bottom: 0rem !important; }

    /* Kutuların Grid Düzeni */
    .indicator-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 15px; }
    .metric-card { background-color: #162a26; border: 1px solid #1f3d37; border-radius: 12px; padding: 15px; }
    .indicator-title { font-size: 11px; color: #88c0b0 !important; margin-bottom: 2px; text-align: left; }
    .indicator-value { font-size: 17px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
    
    /* Durum Kutucukları */
    .status-box { background-color: #0d1a17; border-radius: 4px; font-size: 10px; padding: 3px 8px; margin-top: 10px; color: #88c0b0; text-align: center; border: 1px solid #1f3d37; }
    .status-al { background-color: #00ff88; color: #000 !important; font-weight: bold; border: none; }
    .status-sat { background-color: #ff4b4b; color: white !important; font-weight: bold; border: none; }

    /* Sol Panel */
    .left-panel { background-color: #0d1a17; padding: 25px 15px; border-radius: 15px; text-align: center; border: 1px solid #1f3d37; }
    .price-text { font-size: 42px; font-weight: bold; color: white; margin: 15px 0; white-space: nowrap; }
    .sig-box { padding: 15px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-top: 20px; }
    .sig-al { background-color: #00ff88; color: #00331a; }
    .sig-sat { background-color: #ff4b4b; color: white; }
    .sig-notr { background-color: #3d4d49; color: white; }

    /* TELEFONLAR İÇİN ÖZEL DÜZENLEME */
    @media (max-width: 768px) {
        .indicator-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; }
        .price-text { font-size: 32px !important; }
        .block-container { padding-top: 2rem !important; }
        .left-panel { margin-bottom: 20px; }
    }
    /* Mobildeki menü kutusunun içini ve yazısını zorla karartır */
    div[data-baseweb="select"] > div {
        background-color: #162a26 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ ÇEKME ---
@st.cache_data(ttl=600)
def veri_getir(sembol):
    try:
        df = yf.download(sembol, period="1y", interval="1d", auto_adjust=True, timeout=20)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

st.sidebar.header("🔍 Kontrol Paneli")
izleme_input = st.sidebar.text_input("Hisseler:", "BIMAS.IS, MIATK.IS, THYAO.IS, PGSUS.IS, KFEIN.IS")
hisseler = [h.strip() for h in izleme_input.split(",")]
secilen_hisse = st.sidebar.selectbox("Hisse Seç:", hisseler)

data = veri_getir(secilen_hisse)

if not data.empty:
    # --- TEKNİK HESAPLAMALAR ---
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['SMA_50'] = ta.sma(data['Close'], length=50)
    macd = ta.macd(data['Close'])
    data['MACD_VAL'] = macd.iloc[:, 0]
    stoch = ta.stoch(data['High'], data['Low'], data['Close'])
    data['STOCH_VAL'] = stoch.iloc[:, 0]
    bbands = ta.bbands(data['Close'], length=20)
    data['BBL'] = bbands.iloc[:, 0]
    data['BBU'] = bbands.iloc[:, 2]
    data['MOM'] = ta.mom(data['Close'], length=10)
    
    data = data.ffill()

    # Değerleri Al
    son_fiyat = float(data['Close'].iloc[-1])
    gecmis_fiyat = float(data['Close'].iloc[-2])
    degisim = ((son_fiyat - gecmis_fiyat) / gecmis_fiyat) * 100
    rsi_val = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50.0
    sma_val = float(data['SMA_50'].iloc[-1]) if not pd.isna(data['SMA_50'].iloc[-1]) else son_fiyat
    macd_val = float(data['MACD_VAL'].iloc[-1]) if not pd.isna(data['MACD_VAL'].iloc[-1]) else 0.0
    stoch_val = float(data['STOCH_VAL'].iloc[-1]) if not pd.isna(data['STOCH_VAL'].iloc[-1]) else 50.0
    mom_val = float(data['MOM'].iloc[-1]) if not pd.isna(data['MOM'].iloc[-1]) else 0.0
    bbl_val = float(data['BBL'].iloc[-1]) if not pd.isna(data['BBL'].iloc[-1]) else son_fiyat
    bbu_val = float(data['BBU'].iloc[-1]) if not pd.isna(data['BBU'].iloc[-1]) else son_fiyat

    sinyal_text, sinyal_class = "NÖTR", "sig-notr"
    if rsi_val < 38 and son_fiyat > sma_val: sinyal_text, sinyal_class = "AL SİNYALİ", "sig-al"
    elif rsi_val > 68: sinyal_text, sinyal_class = "SAT SİNYALİ", "sig-sat"

    # --- 3. ANA YERLEŞİM ---
    col_left, col_right = st.columns([1, 3.5]) 

    with col_left:
        st.markdown(f"""<div class="left-panel">
            <h1 style='color:#00d1ff; font-size:32px;'>{secilen_hisse.split('.')[0]}</h1>
            <div class="price-text">₺{son_fiyat:.2f}</div>
            <div style='color: {"#00ff88" if degisim > 0 else "#ff4b4b"}; font-size: 18px;'>{"▲" if degisim > 0 else "▼"} %{degisim:.2f}</div>
            <div class="sig-box {sinyal_class}">{sinyal_text}</div>
            <p style='color:#4a6b63; margin-top:20px; font-size:10px;'>{datetime.now().strftime('%d %b %Y, %H:%M')}</p>
        </div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown(f"""
        <div class="indicator-grid">
            <div class="metric-card"><div class="indicator-title">RSI (14)</div><div class="indicator-value"><span>Momentum</span><span>{rsi_val:.1f}</span></div><div class="status-box">{"AŞIRI ALIM" if rsi_val>70 else "NÖTR"}</div></div>
            <div class="metric-card"><div class="indicator-title">Trend (SMA)</div><div class="indicator-value"><span>50 Günlük</span><span>{"Yükseliş" if son_fiyat>sma_val else "Düşüş"}</span></div><div class="status-box {"status-al" if son_fiyat>sma_val else "status-sat"}">{"AL" if son_fiyat>sma_val else "SAT"}</div></div>
            <div class="metric-card"><div class="indicator-title">MACD</div><div class="indicator-value"><span>Trend</span><span>{macd_val:.2f}</span></div><div class="status-box">{"POZİTİF" if macd_val>0 else "NEGATİF"}</div></div>
            <div class="metric-card"><div class="indicator-title">Bollinger</div><div class="indicator-value"><span>Volatilite</span><span>{"Üst" if son_fiyat>bbu_val else "NÖTR"}</span></div><div class="status-box">NÖTR</div></div>
            <div class="metric-card"><div class="indicator-title">Stokastik</div><div class="indicator-value"><span>Osilatör</span><span>{stoch_val:.1f}</span></div><div class="status-box">{"DOYMUŞ" if stoch_val>80 else "NÖTR"}</div></div>
            <div class="metric-card"><div class="indicator-title">Momentum</div><div class="indicator-value"><span>İvme</span><span>%{mom_val:.1f}</span></div><div class="status-box">{"ARTIYOR" if mom_val>0 else "AZALIYOR"}</div></div>
        </div>
        """, unsafe_allow_html=True)

        # GRAFİK KİLİTLEME (Parmakla dokunulduğunda bozulmaz)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Fiyat'))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50', line=dict(color='#ffaa00', width=1.5)))
        
        fig.update_layout(
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0),
            dragmode=False, # Grafiği parmakla kaydırmayı kapatır
            hovermode='x unified' # Dokunulduğunda veriyi gösterir ama grafiği bozmaz
        )
        
        st.plotly_chart(fig, use_container_width=True, config={
            'staticPlot': False, 
            'scrollZoom': False, 
            'displayModeBar': False,
            'doubleClick': 'reset'
        })

