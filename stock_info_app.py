import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO

# ----------------------------------------
# 한국 주식 종목 코드를 가져오는 함수
# ----------------------------------------


def get_stock_info(market_type=None):
    base_url = "https://kind.krx.co.kr/corpgeneral/corpList.do"
    method = "download"

    if market_type == 'kospi':
        marketType = 'stockMkt'
    elif market_type == 'kosdaq':
        marketType = 'kosdaqMkt'
    else:
        marketType = ''

    url = "{0}?method={1}&marketType={2}".format(base_url, method, marketType)

    df = pd.read_html(url, header=0)[0]

    # 종목코드 열을 6자리 숫자로 표시된 문자열로 변환
    df['종목코드'] = df['종목코드'].apply(lambda x: f"{x:06d}")
    df = df[['회사명', '종목코드']]

    return df


# ----------------------------------------------------
# yfinance에 이용할 Ticker 심볼을 반환하는 함수
# ----------------------------------------------------
def get_ticker_symbol(company_name, market_type):
    df = get_stock_info(market_type)

    code = df[df['회사명'] == company_name]['종목코드'].values
    code = code[0]

    if market_type == 'kospi':
        ticker_symbol = code + ".KS"
    elif market_type == 'kosdaq':
        ticker_symbol = code + ".KQ"

    return ticker_symbol


st.title("주식 정보를 가져오는 웹앱")

st.sidebar.header("회사 이름과 기간 입력")
stock_name = st.sidebar.text_input('회사 이름', value="NAVER")
type_options = ['kospi', 'kosdaq']
stock_type = st.sidebar.radio('코스피/코스닥', type_options)
date_range = st.sidebar.date_input(
    '기간', value=[datetime.date(2019, 1, 1), datetime.date(2021, 12, 31)])

clicked = st.sidebar.button('주가 데이터 가져오기')
if clicked:
    # 인자로 주식 종목 이름(stock_name)과 마켓 타입(stock_type) 전달
    ticker_symbol = get_ticker_symbol(stock_name, stock_type)

    # 인자로 ticker_symbol 전달
    ticker_data = yf.Ticker(ticker_symbol)

    # 종료일은 date_range 변수에 담긴 값에 하루를 더해주기
    start_p = date_range[0]
    end_p = date_range[1]+datetime.timedelta(days=1)

    df = ticker_data.history(start=start_p, end=end_p)

    st.subheader(f"[{stock_name}] 주가데이터")
    st.dataframe(df.head())

    # Matplotlib으로 그래프를 그리기 위한 코드
    matplotlib.rcParams['font.family'] = 'Malgun Gothic'
    matplotlib.rcParams['axes.unicode_minus'] = False

    ax = df['Close'].plot(grid=True, figsize=(15, 5))
    ax.set_title("주가(종가) 그래프", fontsize=30)
    ax.set_xlabel("기간", fontsize=20)
    ax.set_ylabel("주가(원)", fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    fig = ax.get_figure()

    st.pyplot(fig)

    st.markdown("**주가 데이터** 다운로드")

    csv_data = df.to_csv()

    excel_data = BytesIO()  # 메모리 버퍼에 바이너리 객체 생성
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    df.set_index('Date', inplace=True)
    df.to_excel(excel_data)  # DataFrame 데이터를 엑셀 형식으로 버퍼에 쓰기

    colums = st.columns(2)
    with colums[0]:
        st.download_button('CSV 파일 다운로드', csv_data, file_name='stock_data.csv')

    with colums[1]:
        st.download_button('Excel 파일 다운로드', excel_data,
                           file_name='excel_data.csv')
