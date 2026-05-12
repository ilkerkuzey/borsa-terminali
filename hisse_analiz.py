import os, subprocess, sys
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import yfinance
    import pandas_ta
except ImportError:
    install('yfinance')
    install('pandas-ta')
    install('plotly')
import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SAYFA VE ÖZEL CSS TASARIMI ---
st.set_page_config(page_title="AI Teknik Analiz", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b1e1a; padding: 10px; }
    
    /* Sağ paneldeki 6 kutulu ızgara düzeni */
    .indicator-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-bottom: 15px;
    }
    
    .metric-card { 
        background-color: #162a26; 
        border: 1px solid #1f3d37; 
        border-radius: 12px; 
        padding: 15px; 
        color: white;
    }
    
    .indicator-title { font-size: 11px; color: #88c0b0; margin-bottom: 2px; opacity: 0.8; text-align: left; }
    .indicator-value { font-size: 17px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
    .status-box { background-color: #0d1a17; border-radius: 4px; font-size: 10px; padding: 3px 8px; margin-top: 10px; color: #88c0b0; text-align: center; border: 1px solid #1f3d37; }
    .status-al { background-color: #00ff88; color: #000 !important; font-weight: bold; border: none; }
    .status-sat { background-color: #ff4b4b; color: white !important; font-weight: bold; border: none; }

    /* Sol Panel */
    .left-panel { 
        background-color: #0d1a17; 
        padding: 30px 20px; 
        border-radius: 15px; 
        text-align: center; 
        border: 1px solid #1f3d37;
        height: 100%;
    }
    .price-text { font-size: 45px; font-weight: bold; color: white; margin: 15px 0; white-space: nowrap; }
    .sig-box { padding: 15px; border-radius: 10px; font-size: 20px; font-weight: bold; margin-top: 20px; }
    .sig-al { background-color: #00ff88; color: #00331a; }
    .sig-sat { background-color: #ff4b4b; color: white; }
    .sig-notr { background-color: #3d4d49; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ ÇEKME ---
@st.cache_data
def veri_getir(sembol):
    df = yf.download(sembol, period="1y", interval="1d", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

st.sidebar.header("🔍 Kontrol Paneli")
izleme_listesi = st.sidebar.text_input("Hisseler:", "BIMAS.IS, MIATK.IS, THYAO.IS, PGSUS.IS", KFEIN.IS", TEHOL.IS", MGROS.IS")
secilen_hisse = st.sidebar.selectbox("Hisse Seç:", [h.strip() for h in izleme_listesi.split(",")])

data = veri_getir(secilen_hisse)

if not data.empty:
    # Teknik Hesaplamalar
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

    # Son Değerler
    son_fiyat = float(data['Close'].values[-1])
    rsi_val = float(data['RSI'].dropna().values[-1]) if not data['RSI'].dropna().empty else 50.0
    sma_val = float(data['SMA_50'].dropna().values[-1]) if not data['SMA_50'].dropna().empty else son_fiyat
    macd_val = float(data['MACD_VAL'].dropna().values[-1]) if not data['MACD_VAL'].dropna().empty else 0.0
    stoch_val = float(data['STOCH_VAL'].dropna().values[-1]) if not data['STOCH_VAL'].dropna().empty else 50.0
    mom_val = float(data['MOM'].dropna().values[-1]) if not data['MOM'].dropna().empty else 0.0
    bbl_val = float(data['BBL'].dropna().values[-1]) if not data['BBL'].dropna().empty else son_fiyat
    bbu_val = float(data['BBU'].dropna().values[-1]) if not data['BBU'].dropna().empty else son_fiyat

    # Sinyal Mantığı
    sinyal_text, sinyal_class = "NÖTR", "sig-notr"
    if rsi_val < 38 and son_fiyat > sma_val: sinyal_text, sinyal_class = "AL SİNYALİ", "sig-al"
    elif rsi_val > 68: sinyal_text, sinyal_class = "SAT SİNYALİ", "sig-sat"

    # --- 3. ANA YERLEŞİM ---
    col_left, col_right = st.columns([1, 3.5]) 

    with col_left:
        st.markdown(f"""<div class="left-panel">
            <h1 style='color:#00d1ff; font-size:32px;'>{secilen_hisse.split('.')[0]}</h1>
            <p style='color:#88c0b0; font-size:12px;'>{secilen_hisse}</p>
            <div class="price-text">₺{son_fiyat:.2f}</div>
            <div style='color:#4a6b63;'>━━━━ ● ━━━━</div>
            <div class="sig-box {sinyal_class}">{sinyal_text}</div>
            <p style='color:#4a6b63; margin-top:40px; font-size:10px;'>{datetime.now().strftime('%d %b %Y, %H:%M')}</p>
        </div>""", unsafe_allow_html=True)

    with col_right:
        # 6 KUTUYU BURADA SABİTLİYORUZ
        st.markdown(f"""
        <div class="indicator-grid">
            <div class="metric-card">
                <div class="indicator-title">RSI (14)</div>
                <div class="indicator-value"><span>Momentum</span><span>{rsi_val:.1f}</span></div>
                <div class="status-box">{"AŞIRI ALIM" if rsi_val>70 else "NÖTR"}</div>
            </div>
            <div class="metric-card">
                <div class="indicator-title">Trend (SMA)</div>
                <div class="indicator-value"><span>50 Günlük</span><span>{"Yükseliş" if son_fiyat>sma_val else "Düşüş"}</span></div>
                <div class="status-box {"status-al" if son_fiyat>sma_val else "status-sat"}">{"AL" if son_fiyat>sma_val else "SAT"}</div>
            </div>
            <div class="metric-card">
                <div class="indicator-title">MACD</div>
                <div class="indicator-value"><span>Trend Gücü</span><span>{macd_val:.2f}</span></div>
                <div class="status-box">{"POZİTİF" if macd_val>0 else "NEGATİF"}</div>
            </div>
            <div class="metric-card">
                <div class="indicator-title">Bollinger</div>
                <div class="indicator-value"><span>Volatilite</span><span>{"Üst Bant" if son_fiyat>bbu_val else "NÖTR"}</span></div>
                <div class="status-box">NÖTR</div>
            </div>
            <div class="metric-card">
                <div class="indicator-title">Stokastik</div>
                <div class="indicator-value"><span>Osilatör</span><span>{stoch_val:.1f}</span></div>
                <div class="status-box">{"DOYMUŞ" if stoch_val>80 else "NÖTR"}</div>
            </div>
            <div class="metric-card">
                <div class="indicator-title">Momentum</div>
                <div class="indicator-value"><span>İvme</span><span>%{mom_val:.1f}</span></div>
                <div class="status-box">{"ARTIYOR" if mom_val>0 else "AZALIYOR"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Grafik Alanı
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Fiyat'))
        fig.add_trace(go.Scatter(x=data.index, y=data['SMA_50'], name='SMA 50', line=dict(color='#ffaa00', width=1.8)))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Veri yüklenemedi.")
